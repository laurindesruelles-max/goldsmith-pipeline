import sys, os, json, math, random, subprocess, numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import case as C
import effects as E
from case import W, H, FPS, font, F_ANTON, F_SERIF, F_SERIF4, F_TYPE, F_SANS, GOLD, IVORY, RED, INK, ease, eout, view

TM = json.load(open("timing.json")); SC = {s["n"]: s for s in json.load(open("../scenes.json"))}
SPEC = json.load(open("spec.json")) if os.path.exists("spec.json") else {}

# ---- Spannungspausen ("beats"): Stille nach dem Satz mit dem Anker einfügen ----
# spec.json: "beats": {"3": [["It isn't.", 1.2]], ...}  -> Pause nach diesem Satz, Musik taucht ab, danach Hit
BEATS = {}   # n -> [(t_in_scene, gap)]
def _raw_wt(n, anchor):
    vo = SC[n]["vo"]; i = vo.lower().find(anchor.lower())
    if i < 0: raise ValueError(f"beat anchor not found {n}: {anchor}")
    segs = TM[str(n)]["segs"]; tot = sum(b-a for a, b in segs); target = tot*i/len(vo)
    for a, b in segs:
        if target <= b-a: return a+target
        target -= b-a
    return segs[-1][1]
for k, lst in SPEC.get("beats", {}).items():
    n = int(k); ins = []
    for anchor, gap in lst:
        t = _raw_wt(n, anchor); segs = TM[str(n)]["segs"]
        b = next((e for a, e in segs if e >= t), segs[-1][1]); ins.append((b, float(gap)))
    ins.sort(); shift = 0.0; newsegs = []
    for a, e in TM[str(n)]["segs"]:
        newsegs.append([a+shift, e+shift])
        for b, gap in ins:
            if abs(e-b) < 1e-6: shift += gap
    TM[str(n)]["segs"] = newsegs; TM[str(n)]["dur"] += sum(g for _, g in ins)
    # build voice file with inserted silence
    os.makedirs("build/vo", exist_ok=True); src = f"../audio/{n}.wav"; parts = []; last = 0.0
    for i2, (b, gap) in enumerate(ins):
        parts.append(f"[0:a]atrim={last}:{b},asetpts=PTS-STARTPTS[p{i2}];aevalsrc=0:d={gap}:s=48000:c=stereo[g{i2}]")
        last = b
    chain = "".join(f"[p{i}][g{i}]" for i in range(len(ins)))
    flt = "[0:a]aresample=48000,aformat=channel_layouts=stereo,asplit=%d%s;" % (len(ins)+1, "".join(f"[s{i}]" for i in range(len(ins)+1)))
    segs_f = []; last = 0.0
    for i2, (b, gap) in enumerate(ins):
        segs_f.append(f"[s{i2}]atrim={last}:{b},asetpts=PTS-STARTPTS[p{i2}];aevalsrc=0|0:d={gap}:s=48000[g{i2}]"); last = b
    segs_f.append(f"[s{len(ins)}]atrim={last},asetpts=PTS-STARTPTS[pe]")
    flt += ";".join(segs_f) + ";" + chain + f"[pe]concat=n={2*len(ins)+1}:v=0:a=1[o]"
    subprocess.run(["ffmpeg","-y","-loglevel","error","-i",src,"-filter_complex",flt,"-map","[o]",f"build/vo/{n}.wav"], check=True)
    BEATS[n] = ins
FIRST = int(os.environ.get("FIRST_SCENE", "9"))   # 9 = Video 001 (handgebauter Cold Open 1-8); neue Videos: 1
LAST = max(SC)
START = C.TOTAL if FIRST > 1 else 0.0
PLAN2 = []; S0 = {}; acc = START
for n in range(FIRST, LAST+1):
    T = round((TM[str(n)]["dur"] + (1.6 if n == LAST else 0.4))*FPS)/FPS
    PLAN2.append((n, T)); S0[n] = acc; acc += T
END = acc
def dips():
    """globale Zeitfenster der Spannungspausen (für Musik-Abtauchen + Hit)"""
    out = []
    for n, ins in BEATS.items():
        if n in S0:
            sh = 0.0
            for b, gap in ins: out.append([S0[n]+b+sh, S0[n]+b+sh+gap]); sh += gap
    return out
def music_cues():
    """[(globale Startzeit, track)] aus spec.json "music": {"1": "crime_archive", "9": "suspense_pulse"}"""
    m = SPEC.get("music") or {str(FIRST): "crime_archive"}
    return sorted((S0.get(int(k), START), v) for k, v in m.items() if int(k) in S0 or int(k) <= FIRST)

def wt(n, anchor):
    """estimated start time of anchor phrase inside scene n (proportional over speech)."""
    vo = SC[n]["vo"]; i = vo.lower().find(anchor.lower())
    if i < 0: raise ValueError(f"anchor not found {n}: {anchor}")
    segs = TM[str(n)]["segs"]; tot = sum(b-a for a, b in segs); target = tot*i/len(vo)
    for a, b in segs:
        if target <= b-a: return a+target
        target -= b-a
    return segs[-1][1]

CH = {13: ("CHAPTER 2", "OWNING THE ROAD"), 24: ("CHAPTER 3", "THE OAKLEY WAR"), 33: ("CHAPTER 4", "THE CLOSED LOOP"),
      42: ("CHAPTER 5", "THE GIANT GETS BIGGER"), 49: ("PART 6", "THE CATCH"), 54: ("FINAL", "THE VERDICT")}
def chapter_of(n):
    lab = "CHAPTER 1  ·  THE ORPHAN"
    for k in sorted(CH):
        if n >= k: lab = f"{CH[k][0]}  ·  {CH[k][1]}"
    return lab

# overlay spec: (kind, anchor, payload)
S = {
 9: [("typed", "By fourteen", ["AGE: 14", "TOOL & DIE APPRENTICE"]), ("pop", "including parts", "EYEGLASS FRAMES.")],
 10: [("map", "In 1961", (0.66, 0.30)), ("typed", "In 1961", ["AGORDO, DOLOMITES", "1961"]), ("pop", "He called it", "LUXOTTICA.", GOLD)],
 11: [("pop", "parts for other", "PARTS FOR OTHERS."), ("typed", "By 1971", ["1971", "OWN-BRAND FRAMES"])],
 12: [("pop", "Why only", "WHY ONLY MAKE THE GLASSES?"), ("pop", "own every step", "OWN EVERY STEP.", GOLD)],
 13: [("typed", "In 1974", ["1974", "FIRST DISTRIBUTOR"]), ("typed", "In 1981", ["1981", "FIRST SUBSIDIARY: GERMANY"])],
 14: [("typed", "in 1988", ["1988", "LICENSE: GIORGIO ARMANI"]), ("stamp", "Giorgio Armani", "SIGNED")],
 15: [("pop", "medical device", "NOT A MEDICAL DEVICE."), ("pop", "They became fashion", "FASHION.", GOLD), ("pop", "priced like jewelry", "PRICED LIKE JEWELRY.", GOLD)],
 16: [("pop", "shopping spree", "THE SHOPPING SPREE."), ("typed", "In 1995", ["1995", "LENSCRAFTERS"]), ("stamp", "North America", "ACQUIRED")],
 17: [("typed", "In 1999", ["1999", "RAY-BAN"]), ("counter", "640 million", ("$", 640, "M", "PAID TO BAUSCH & LOMB"))],
 18: [("pop", "in trouble", "RAY-BAN WAS IN TROUBLE."), ("counter", "as little as", ("$", 20, "", "BARGAIN-BIN PRICE"))],
 19: [("pop", "fixed the quality", "BETTER QUALITY."), ("pop", "raised the price", "HIGHER PRICE.", GOLD), ("pop", "far more profit", "FAR MORE PROFIT.", GOLD)],
 20: [("typed", "In 2001", ["2001", "SUNGLASS HUT"]), ("stamp", "the biggest", "ACQUIRED")],
 21: [("chain", "designed the product", [("DESIGN", "designed"), ("MAKE", "made it"), ("SHIP", "shipped"), ("SELL", "sold it")])],
 22: [("pop", "different company", "EVERY STEP = A MARGIN."), ("pop", "same pocket", "ONE POCKET.", GOLD)],
 23: [("pop", "the power to decide", "WHO GETS SEEN.", GOLD)],
 24: [("typed", "in 1975", ["1975", "A GARAGE IN CALIFORNIA"]), ("counter", "300 dollars", ("$", 300, "", "STARTING CAPITAL"))],
 25: [("pop", "athletes loved", "ATHLETES LOVED IT."), ("pop", "a real competitor", "A REAL COMPETITOR.", GOLD)],
 26: [("typed", "In 1996", ["1996", "PRICE DISPUTE"]), ("stamp", "stopped carrying", "DROPPED"), ("counter", "dropped by a third", ("-", 33, "%", "OAKLEY'S MARKET VALUE"))],
 27: [("typed", "in 2001", ["2001", "SUNGLASS HUT"]), ("stamp", "pushed off", "REMOVED")],
 28: [("pop", "It sued", "OAKLEY SUES."), ("stamp", "won a court order", "COURT ORDER")],
 29: [("typed", "By late 2001", ["LATE 2001", "TRUCE"]), ("pop", "owned the stores", "WHOEVER OWNS THE STORES"), ("pop", "Luxottica's hands", "HOLDS THE POWER.", GOLD)],
 30: [("typed", "In 2007", ["2007", "OFFER FOR OAKLEY"]), ("counter", "2.1 billion", ("$", 2.1, "B", "PURCHASE PRICE")), ("stamp", "let the deal", "APPROVED")],
 31: [("pop", "refused to bend", "THE RIVAL..."), ("stamp", "now belonged", "ACQUIRED")],
 32: [("pop", "isn't a brand", "NOT A BRAND."), ("pop", "employee benefits", "YOUR EMPLOYEE BENEFITS.", GOLD)],
 33: [("pop", "under license", "UNDER LICENSE.", GOLD)],
 34: [("brands", "Chanel", ["Chanel", "Prada", "Armani", "Burberry", "Versace", "Dolce", "Michael Kors", "Coach", "Tiffany"]), ("stamp", "same group", "SAME GROUP")],
 35: [("pop", "competing", "\"COMPETING\" BRANDS?"), ("pop", "same factories", "SAME FACTORIES.", GOLD)],
 36: [("typed", "owns EyeMed", ["OWNED BY THE GROUP:", "EYEMED VISION CARE"]), ("pop", "biggest vision insurance", "VISION INSURANCE.", GOLD)],
 37: [("chain", "employer pays", [("EMPLOYER", "employer pays"), ("INSURANCE", "plan's network"), ("STORE", "stores run by"), ("FRAMES", "selling its frames")])],
 38: [("pop", "To be fair", "TO BE FAIR..."), ("pop", "follow the money", "FOLLOW THE MONEY.", GOLD)],
 39: [("words", "Insurer", [("INSURER.", "Insurer"), ("STORE.", "Store."), ("BRAND.", "Brand."), ("FACTORY.", "Factory.")]), ("pop", "One company", "ONE COMPANY.", (220, 40, 45))],
 40: [("typed", "In 2012", ["2012", "60 MINUTES"]), ("quote", "Everything is worth", ("“Everything is worth what", "people are ready to pay.”", "ANDREA GUERRA, THEN-CEO OF LUXOTTICA"))],
 41: [("counter", "twenty times", ("×", 20, "", "PRICE VS. PRODUCTION COST"))],
 42: [("typed", "In 2018", ["2018", "ESSILOR + LUXOTTICA"]), ("pop", "Frames and lenses", "FRAMES + LENSES.", GOLD), ("counter", "70 billion", ("$", 70, "B", "COMBINED VALUE"))],
 43: [("typed", "died in 2022", ["2022", "AGE 87"]), ("counter", "25 billion", ("$", 25, "B", "PERSONAL FORTUNE")), ("pop", "built an empire", "AN EMPIRE.", GOLD)],
 44: [("counter", "3,000", ("", 3000, "+", "SUNGLASS HUT STORES")), ("pop", "thousands of other", "+ THOUSANDS MORE.")],
 45: [("typed", "In 2025", ["2025", "ANNUAL REVENUE"]), ("counter", "28.5 billion", ("€", 28.5, "B", "REVENUE")), ("stamp", "a record", "RECORD")],
 46: [("typed", "In 2024", ["2024", "SUPREME"]), ("counter", "1.5 billion", ("$", 1.5, "B", "PURCHASE PRICE"))],
 47: [("pop", "a new partner", "NEW PARTNER: META.", GOLD), ("counter", "7 million", ("", 7, "M+", "AI GLASSES SOLD IN 2025"))],
 48: [("counter", "three billion", ("€", 3, "B", "META'S STAKE"))],
 49: [("pop", "uncomfortable part", "THE UNCOMFORTABLE PART."), ("pop", "business schools", "BUSINESS SCHOOLS WOULD ADMIRE IT.", GOLD)],
 50: [("pop", "rescued brands", "RESCUED BRANDS."), ("pop", "bargain bins", "FROM BARGAIN BINS..."), ("pop", "an icon again", "...TO AN ICON.", GOLD)],
 51: [("chain", "makes the product", [("PRODUCT", "makes the product"), ("STORE", "owns the store"), ("INSURER", "runs one of")]), ("pop", "get a lot weaker", "COMPETITION GETS WEAKER.", (220, 40, 45))],
 52: [("pop", "different shapes", "DIFFERENT LOGOS."), ("pop", "same place", "SAME MONEY.", GOLD)],
 53: [("pop", "cameras and AI", "CAMERAS. AI."), ("pop", "teamed up", "+ BIG TECH.", GOLD)],
 54: [("pop", "look past the logo", "LOOK PAST THE LOGO.", GOLD)],
 55: [("pop", "Independent brands", "INDEPENDENT OPTICIANS."), ("pop", "fraction of the price", "A FRACTION OF THE PRICE.", GOLD), ("pop", "harder to find", "HARDER TO FIND.")],
 56: [("pop", "between brands", "BRANDS..."), ("pop", "price tags", "...OR PRICE TAGS?", GOLD)],
 57: [("stamp", "Now that you know", "CASE CLOSED"), ("typed", "Tell me", ["TELL ME IN THE COMMENTS"])],
}
# optional: spec.json im Arbeitsordner ersetzt S und CH (neue Videos)
if os.path.exists("spec.json"):
    _sp = json.load(open("spec.json"))
    S = {int(k): [tuple(o[:3]) + ((tuple(o[3]),) if len(o) > 3 else ()) for o in v] for k, v in _sp["scenes"].items()}
    CH = {int(k): tuple(v) for k, v in _sp.get("chapters", {}).items()}
# resolve
EV = {}
for n, ov in S.items():
    lst = []
    for o in ov:
        t = wt(n, o[1])
        if o[0] in E.RENDER and t < 1.0: t = 0.0   # Vollbild-Effekt ab Szenenstart: kein kurzes Aufblitzen des Grundbilds davor
        lst.append((o[0], t) + tuple(o[2:]))
    EV[n] = lst
    if n in CH:  # shift nothing; chapter card overlays first 2.1s
        pass

# shots: cut on sentence starts (min 2.6s apart)
PRESETS = [((0.5, 0.5, 1.0), (0.5, 0.48, 1.12)), ((0.36, 0.46, 1.5), (0.42, 0.46, 1.6)), ((0.64, 0.55, 1.45), (0.58, 0.52, 1.35)),
           ((0.5, 0.42, 1.7), (0.5, 0.45, 1.85)), ((0.3, 0.6, 1.4), (0.38, 0.55, 1.4)), ((0.7, 0.4, 1.35), (0.62, 0.45, 1.5))]
def shots(n, T):
    vo = SC[n]["vo"]; cuts = [0.0]
    for i, ch in enumerate(vo[:-3]):
        if ch in ".?:," and vo[i+1] == " ":
            t = wt(n, vo[i+2:i+22]) - 0.05
            need = 2.6 if ch in ".?" else 3.8          # Komma-Schnitt nur bei langen Einstellungen
            if t-cuts[-1] >= need and T-t >= 2.0: cuts.append(t)
    return cuts
SHOTS = {n: shots(n, T) for n, T in PLAN2}

IMG = {}; MAP = None; CARD = {}
def init():
    global MAP
    C.init()
    MAP = C.IMG["map"]

def card_text(text, w=300, h=110):
    k = (text, w)
    if k not in CARD:
        c = Image.new("RGBA", (w+30, h+30), (0,0,0,0)); sh = Image.new("RGBA", c.size, (0,0,0,0))
        ImageDraw.Draw(sh).rectangle([12, 16, w+12, h+16], fill=(0,0,0,170)); c.alpha_composite(sh.filter(ImageFilter.GaussianBlur(8)))
        d = ImageDraw.Draw(c); d.rectangle([0, 0, w, h], fill=(238,230,206,255)); d.line([(0, 22), (w, 22)], fill=(200,60,60,200), width=2)
        f = font(F_TYPE, 46 if len(text) < 10 else 38); d.text((w/2, h/2+10), text, font=f, fill=INK, anchor="mm")
        CARD[k] = c
    return CARD[k]

def fmt(v, val):
    if isinstance(val, float): return f"{v:.1f}"
    v = int(round(v)); return f"{v:,}" if val >= 1000 else str(v)

def overlays(n, t, T, layer, fr):
    ev = EV.get(n, []); pops = [e for e in ev if e[0] in ("pop", "words")]
    dim = 0.0
    for e in ev:
        kind, t0 = e[0], e[1]
        if kind == "typed":
            nxt = [x[1] for x in ev if x[0] == "typed" and x[1] > t0]; t1 = min(nxt) if nxt else T
            if t0 <= t < t1-0.05: C.typed(layer, t, t0, e[2], (130, 770), size=66)
        elif kind == "pop":
            nxt = [x[1] for x in pops if x[1] > t0]; t1 = min(nxt + [t0+2.6])
            if n in (56,) and e[3:] and t0 == max(x[1] for x in pops): t1 = T
            C.pop_word(layer, t, t0, e[2], color=(e[3] if len(e) > 3 else (255,255,255)), size=128 if len(e[2]) < 22 else 100, t1=t1)
        elif kind == "words":
            for i, (w, a) in enumerate(e[2]):
                ta = wt(n, a); tb = wt(n, e[2][i+1][1]) if i+1 < len(e[2]) else ta+0.8
                C.pop_word(layer, t, ta, w, size=170, y=540, t1=tb);
        elif kind == "stamp":
            C.stamp(layer, t, t0, e[2], (1440, 330), size=130, rot=-10)
        elif kind == "counter":
            pre, val, suf, label = e[2]
            if t0-0.1 <= t < t0+3.0:
                a = ease((t-t0+0.1)/0.25) * (1 if t < t0+2.75 else max(0, (t0+3.0-t)/0.25)); dim = max(dim, 0.55*a)
                p = eout((t-t0)/0.9); v = val*p
                txt = f"{pre}{fmt(v, val)}{suf}"; s = 1.0+0.08*(1-eout((t-t0)/0.3))
                C.shadow_text(layer, (W/2, H/2-30), txt, font(F_ANTON, 230*s), (220,40,45) if pre in ("-", "×") else GOLD, stroke=6, anchor="mm", alpha=int(255*a))
                if t >= t0+0.5:
                    f = font(F_TYPE, 46); d = ImageDraw.Draw(layer); vis = label[:int((t-t0-0.5)*20)]
                    d.text((W/2, H/2+130), vis, font=f, fill=IVORY+(int(255*a),), anchor="mm")
        elif kind == "quote":
            l1, l2, who = e[2]
            if t >= t0:
                a = ease((t-t0)/0.4); dim = max(dim, 0.68*a)
                C.shadow_text(layer, (W/2, H/2-90), l1, font(F_SERIF, 84), GOLD, anchor="mm", alpha=int(255*a))
                C.shadow_text(layer, (W/2, H/2+20), l2, font(F_SERIF, 84), GOLD, anchor="mm", alpha=int(255*a))
                if t >= t0+1.0: C.typed(layer, t, t0+1.0, [who], (W/2-470, H/2+130), size=40, box=False, cursor=False)
        elif kind == "chain":
            items = e[2]; k = len(items); gap = W/(k+1)
            if t >= t0-0.2: dim = max(dim, 0.35*ease((t-t0+0.2)/0.3))
            d = ImageDraw.Draw(layer)
            for i, (lab, a) in enumerate(items):
                ta = wt(n, a); x = gap*(i+1); y = 470
                if t < ta: continue
                if i > 0:
                    px = gap*i; p = eout((t-ta)/0.25)
                    d.line([(px+160, y), (px+160+(x-160-px-160)*p, y)], fill=(205,22,32,255), width=9)
                    if p >= 1: d.polygon([(x-160, y), (x-185, y-16), (x-185, y+16)], fill=(205,22,32,255))
                c = card_text(lab); p = eout((t-ta)/0.14); s = 1+0.4*(1-p)
                cc = c if s == 1 else c.resize((int(c.width*s), int(c.height*s)))
                layer.alpha_composite(cc, (int(x-cc.width/2+8), int(y-cc.height/2+8)))
        elif kind == "brands":
            names = e[2]; times = [wt(n, nm) for nm in names]
            if t >= times[0]-0.1:
                dim = max(dim, 0.6); d = ImageDraw.Draw(layer)
                for i, (nm, ta) in enumerate(zip(names, times)):
                    if t < ta: continue
                    col, row = i % 3, i // 3; x = W/2+(col-1)*520; y = 300+row*190
                    p = eout((t-ta)/0.15); f = font(F_SERIF, int(78*(1+0.5*(1-p))))
                    C.shadow_text(layer, (x, y), nm.upper(), f, IVORY, anchor="mm", alpha=int(255*min(1, p*1.5)))
        elif kind == "map":
            pass
    return dim

CARD_T = 4.4   # Laurin 16.11.: Kapitelkarte 2 s länger stehen lassen
def chapter_card(n, t, layer):
    if n not in CH or t > CARD_T: return 0
    a = ease(t/0.25)*(1 if t < CARD_T-0.4 else max(0, (CARD_T-t)/0.4))
    C.typed(layer, t, 0.15, [CH[n][0]], (W/2-150, 380), size=56, box=False, cursor=False) if a > 0.05 else None
    if t >= 0.6:
        s = 1+0.06*(1-eout((t-0.6)/0.8)); al = int(255*ease((t-0.6)/0.3)*min(1, a*1.2))
        C.shadow_text(layer, (W/2, 540), CH[n][1], font(F_SERIF, 120*s), GOLD, anchor="mm", alpha=al)
        d = ImageDraw.Draw(layer); w = 420*eout((t-0.6)/0.5)
        d.rectangle([W/2-w, 640, W/2+w, 646], fill=RED+(al,))
    if t > CARD_T-0.4:
        arr = np.asarray(layer).copy(); arr[..., 3] = (arr[..., 3]*a).astype(np.uint8); layer.paste(Image.fromarray(arr))
    return 0.82*a

def takeover(n, t):
    T = dict(PLAN2)[n]
    for e in EV.get(n, []):
        if e[0] in E.RENDER:
            d = E.dur_of(e[0], e[2], e[1], T)
            if e[1] <= t < e[1]+d:
                ctx = {"n": n, "img": "../img", "a": "a", "bg": IMG.get(n)}
                r = E.RENDER[e[0]](t-e[1], d, e[2], ctx)
                if r is not None: return r
    return None

def ducks():
    """Zeitfenster der 3D-Szenen (Musik leicht absenken, damit Raumklang hörbar ist)."""
    out = []
    for n, T in PLAN2:
        for e in EV.get(n, []):
            if e[0] in E.DUCK: out.append([S0[n]+e[1], S0[n]+e[1]+E.dur_of(e[0], e[2], e[1], T), 0.6])
            if e[0] in getattr(E, "DATA", ()): out.append([S0[n]+e[1], S0[n]+e[1]+E.dur_of(e[0], e[2], e[1], T), 0.28])
    return out

# 2.5D-Parallaxe statt flachem Zoom (Laurin 16.11.: mehr Bewegung). DEPTH=0 schaltet ab.
import depth25d as D
USE_DEPTH = os.environ.get("DEPTH", "1") == "1"
MOVE_ORDER = ["push", "right", "rise", "left", "orbit", "pull"]
DEP, IMGF, ATMO = {}, {}, {}
import cinemagraph as CG
SUF = ["", "_b", "_c", "_d", "_e"]
def shot_key(n, i):
    """jede Einstellung ein eigenes Bild: n, n_b, n_c ... (fehlt eins: abwechselnd n / n_b)"""
    k = f"{n}{SUF[i]}" if i < len(SUF) else None
    if k and (os.path.exists(f"../img/{k}.png") or os.path.exists(f"../vid/{k}.mp4")): return k
    return f"{n}_b" if i % 2 == 1 and os.path.exists(f"../img/{n}_b.png") else str(n)
VID = {}
def vid_frame(key, u, mv):
    if key not in VID:
        VID.clear(); cap = cv2.VideoCapture(f"../vid/{key}.mp4"); fs = []
        while True:
            ok, f = cap.read()
            if not ok: break
            fs.append(cv2.resize(f[..., ::-1], (int(W*1.08), int(H*1.08)), interpolation=cv2.INTER_CUBIC))
        VID[key] = fs
    fs = VID[key]; f = fs[min(len(fs)-1, int(u*(len(fs)-1)))]
    z = 1.0 + 0.04*u; ox = int((f.shape[1]-W)/2); oy = int((f.shape[0]-H)/2)
    return f[oy:oy+H, ox:ox+W].astype(np.float32)
def frame(n, t, T):
    if n not in IMG: IMG.clear(); IMG[n] = C.load_rgb(f"../img/{n}.png", int(W*1.25), int(H*1.25))
    cuts = SHOTS[n]
    tk = takeover(n, t)
    if tk is not None:
        fr, layer = tk
        if n in CH and CARD_T <= t < CARD_T+4.1: C.chapter(layer, t, CARD_T, chapter_of(n))
        return C.rgba_over(fr, layer), cuts
    i = max(k for k, c in enumerate(cuts) if t >= c); t0 = cuts[i]; t1 = cuts[i+1] if i+1 < len(cuts) else T
    pa, pb = PRESETS[(n*3+i) % len(PRESETS)] if (i > 0 or n % 2) and n != LAST else PRESETS[0]
    s = (t-t0)/(t1-t0)
    c = tuple(x+(y-x)*ease(s) for x, y in zip(pa, pb))
    layer = Image.new("RGBA", (W, H), (0,0,0,0)); dx = dy = 0
    for e in EV.get(n, []):
        if e[0] in ("stamp", "counter"):
            sx, sy = C.shake(t, e[1]+(0.1 if e[0] == "stamp" else 0), 16, 0.35); dx += sx; dy += sy
    mp = [e for e in EV.get(n, []) if e[0] == "map"]
    if mp and t < mp[0][1]+3.6:
        tm = t; c2 = C.cam([(0, (0.55, 0.45, 1.1), 0), (mp[0][1]+0.6, (mp[0][2][0], mp[0][2][1]+0.08, 1.8), 1.2)], tm)
        fr = view(MAP, *c2, dx, dy)
        px = (mp[0][2][0]-(c2[0]-0.5/c2[2]))*c2[2]*W; py = (mp[0][2][1]-(c2[1]-0.5/c2[2]))*c2[2]*H
        C.pin_drop(layer, t, mp[0][1]+0.6, (px, py))
    elif USE_DEPTH:
        mv = D.MOVES[MOVE_ORDER[(n*3+i) % len(MOVE_ORDER)]] if str(n) not in SPEC.get("moves", {}) else D.MOVES[SPEC["moves"][str(n)]]
        key = shot_key(n, i)
        tags = set(SPEC.get("fx", {}).get(str(n), []))
        if SPEC.get("atmo", {}).get(str(n)) == "dust": tags.add("rays")
        u = min(max(s, 0), 1)
        if os.path.exists(f"../vid/{key}.mp4"):              # bereits vorhandener KI-Clip (z. B. Probe) – kostenlos wiederverwenden
            fr = vid_frame(key, u, mv)
        else:
            if key not in IMGF:
                if key == str(n): im = IMG[n]
                else: im = C.load_rgb(f"../img/{key}.png", int(W*1.25), int(H*1.25))
                if len(IMGF) > 4: IMGF.clear(); DEP.clear()
                IMGF[key] = im.astype(np.float32)
                DEP[key] = cv2.resize(D.load_depth(f"../img/{key}_depth.png", im), (im.shape[1], im.shape[0]))
            srcimg = CG.src(IMGF[key], key, t, tags)
            fr = D.frame(srcimg, DEP[key], u, mv, W, H)
        if dx or dy: fr = cv2.warpAffine(fr, np.float32([[1, 0, dx], [0, 1, dy]]), (W, H), borderMode=cv2.BORDER_REFLECT)
        a = SPEC.get("atmo", {}).get(str(n))
        if a:
            if (n, a) not in ATMO: ATMO[(n, a)] = D.Atmo(a, W, H, seed=n)
            fr = ATMO[(n, a)].apply(fr, t)
        if n in SPEC.get("flicker", []): fr = D.flicker(fr, t)
        fr = CG.screen(fr.astype(np.float32), key, t, tags, seed=n)
        fr = fr.astype(np.uint8)
    else:
        fr = view(IMG[n], *c, dx, dy)
    dim = max(overlays(n, t, T, layer, fr), chapter_card(n, t, layer))
    if n in CH and CARD_T <= t < CARD_T+4.1: C.chapter(layer, t, CARD_T, chapter_of(n))
    if dim > 0: fr = (fr*(1-dim)).astype(np.uint8)
    return C.rgba_over(fr, layer), cuts

def post(fr, n, t, cuts):
    g = S0[n]+t
    out = (fr.astype(np.uint16)*C.VIG) >> 8
    fl = 1.0 + 0.025*math.sin(g*17.3)*math.sin(g*5.1)
    out = np.clip((out.astype(np.int16) + C.GRAIN[int(g*FPS) % len(C.GRAIN)])*fl, 0, 255).astype(np.uint8)
    for i, c0 in enumerate(cuts):
        if c0-1.5/FPS <= t < c0: SNAP[(n, i)] = out.copy()
        if i > 0 and c0 <= t < c0+0.5:
            kind = E.trans_kind(n, i)
            if kind: out = E.transition(out, SNAP.get((n, i)), kind, t-c0, seed=n*10+i)
        if c0 <= t < c0+0.2:
            out = view(out, 0.5, 0.5, 1+0.06*(1-(t-c0)/0.2)); break
    # Lichtleck (warmes Filmlicht) an jedem ~3. Schnitt, 0,9 s (Laurin 17.11.: mehr Effekte)
    for i, c0 in enumerate(cuts):
        if SPEC.get("lightleak") and i > 0 and (n*5+i*3) % 3 == 0 and c0 <= t < c0+0.9:   # nicht freigegeben -> nur mit spec "lightleak": true
            u = (t-c0)/0.9; out = light_leak(out, u, seed=n*10+i); break
    return out

_LL = {}
def light_leak(fr, u, seed=0):
    if seed not in _LL:
        r = random.Random(seed); g = np.zeros((H//4, W//4), np.float32)
        for _ in range(3): cv2.circle(g, (r.randint(0, W//4), r.randint(0, H//4)), r.randint(60, 140), 1.0, -1)
        _LL[seed] = (cv2.GaussianBlur(g, (0, 0), 40), r.choice([(255, 140, 60), (255, 90, 50), (255, 190, 110)]), r.choice([-1, 1]))
    g, col, sgn = _LL[seed]
    a = math.sin(u*math.pi)*0.55
    sh = int(sgn*u*W*0.15); m = cv2.resize(np.roll(g, sh//4, axis=1), (W, H))[..., None]*a
    return np.clip(fr.astype(np.float32) + m*np.array(col, np.float32), 0, 255).astype(np.uint8)
SNAP = {}

def render_scene(n):
    T = dict(PLAN2)[n]; tmp = f"build/s{n}.tmp.mp4"
    p = subprocess.Popen(["ffmpeg","-y","-loglevel","error","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-",
                          "-c:v","libx264","-preset","veryfast","-crf","19","-pix_fmt","yuv420p",tmp], stdin=subprocess.PIPE)
    for k in range(int(round(T*FPS))):
        t = k/FPS; fr, cuts = frame(n, t, T); fr = post(fr, n, t, cuts)
        if n == LAST and t > T-1.2: fr = (fr*max(0, (T-t)/1.2)).astype(np.uint8)
        p.stdin.write(fr.tobytes())
    p.stdin.close()
    if p.wait() == 0: os.replace(tmp, f"build/s{n}.mp4")

def sfx_events():
    random.seed(9); ev = []
    for n, T in PLAN2:
        s = S0[n]
        for i, c0 in enumerate(SHOTS[n]):
            if i == 0: continue
            kind = E.trans_kind(n, i)
            # nur Schnitte MIT Übergangseffekt bekommen einen Sound (kein Dauer-Whoosh mehr)
            if kind: ev += [(s+c0, E.TSOUND[kind][0], E.TSOUND[kind][1])]
        for e in EV.get(n, []):
            if e[0] in E.SOUNDFN:
                ev += [(s+e[1]+a, nm, g) for a, nm, g in E.SOUNDFN[e[0]](e[2], E.dur_of(e[0], e[2], e[1], T))]
            if e[0] in E.SOUNDS:
                if e[0] == "parallax" and not os.path.exists(f"../img/{n}_fg.png"): continue
                ev += [(s+e[1]+a, nm, g) for a, nm, g in E.SOUNDS[e[0]]]
        if n in CH:
            # genau EIN Kapitel-Hit, auf der Karte (kein Riser davor)
            ev += [(s+0.6, "braam", 0.9), (s+0.62, "boom", 0.6)]
            C.typed_sfx(ev, s+0.15, [CH[n][0]], gain=0.45)
        for e in EV.get(n, []):
            k, t0 = e[0], s+e[1]
            if k == "typed": C.typed_sfx(ev, t0, e[2], gain=0.5)
            # Schlagwörter/Text-Einblendungen: EIN einzelner Tastenanschlag statt slap (Laurin 17.11.)
            elif k == "pop": ev += [(t0+0.02, "key", 0.6)]
            elif k == "stamp": ev += [(t0+0.1, "stamp", 0.9)]
            elif k == "counter":
                ev += [(t0+i*0.09, "tick", 0.35) for i in range(10)]
                C.typed_sfx(ev, t0+0.5, [e[2][3]], cps=20, gain=0.4)
            elif k == "quote": C.typed_sfx(ev, t0+1.0, [e[2][2]], gain=0.4)
            elif k == "chain":
                for lab, a in e[2]: ev += [(s+wt(n, a), "key", 0.6), (s+wt(n, a), "zip", 0.35)]
            elif k == "brands":
                for nm in e[2]: ev += [(s+wt(n, nm), "key", 0.6)]
            elif k == "words":
                for w, a in e[2]: ev += [(s+wt(n, a), "key", 0.6)]
            elif k == "map": ev += [(t0+0.6, "pin", 0.9)]
    chs = [S0[n] for n in CH if n in S0]
    for a, b in dips():
        # Pause direkt vor einem Kapitel: kein eigener Hit, sonst doppelt mit der Kapitelkarte
        if any(0 <= c - b < 4.0 for c in chs): continue
        pass   # Laurin 16.11.: Bass-Hit (braam/boom) NUR bei Kapiteln
    return ev

if __name__ == "__main__":
    os.makedirs("build", exist_ok=True)
    if sys.argv[1] == "still":
        init()
        for spec in sys.argv[2:]:
            n, t = spec.split("@"); n = int(n); t = float(t); fr, cuts = frame(n, t, dict(PLAN2)[n])
            Image.fromarray(post(fr, n, t, cuts)).save(f"build/p2_{n}_{t}.jpg", quality=85)
    elif sys.argv[1] == "scene":
        init()
        for n in sys.argv[2:]: render_scene(int(n)); print("scene", n, flush=True)
    elif sys.argv[1] == "meta":
        json.dump({"plan": PLAN2, "sfx": sfx_events(), "end": END, "dips": dips(), "ducks": ducks(), "music": music_cues(), "rests": [[S0[int(k)]+v[0], S0[int(k)]+v[0]+v[1]] for k, v in SPEC.get("music_rests", {}).items() if int(k) in S0], "events": {k: [list(map(str, e)) for e in v] for k, v in EV.items()}}, open("build/meta2.json", "w"))
        print(len(PLAN2), END)
