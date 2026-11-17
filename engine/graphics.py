"""Animierte Daten-Grafiken (Laurin 16.11.: mehr Bewegung + Diagramme). Kostenlos, alles prozedural.
Kinds (spec.json, Vollbild, Dauer default 5.5 s oder "dur"):
  ["bars", anchor, {"title": "...", "items": [["PS5", 703, "$703M"], ["XBOX", 239, "$239M"]], "hl": 0, "source": "..."}]
  ["breakdown", anchor, {"total": 80, "parts": [["PLATFORM", 24, "30%"], ["TAKE-TWO", 56, "70%"]], "hl": 0|1|None, "note": "..."}]
  ["timeline", anchor, {"title": "...", "steps": [["2025", "PLANNED", "x"], ["MAY 2026", "DELAYED", "x"], ["NOV 19, 2026", "LAUNCH", "ok"]]}]
  ["flow", anchor, {"nodes": ["YOU", "CONSOLE STORE", "SONY / MICROSOFT", "TAKE-TWO"], "labels": ["$80", "30%", "70%"]}]
Hintergrund = abgedunkeltes, unscharfes Szenenbild, das langsam driftet (nie Standbild).
"""
import math, numpy as np, cv2
from PIL import Image, ImageDraw, ImageFilter
from effects import W, H, f, ANTON, TYPE, INTER, GOLD, IVORY, RED, ease, eout, empty, view, source_line

TEAL = (70, 200, 220); GREEN = (60, 190, 110); GREY = (150, 150, 150)
_BG = {}

def bg(ctx, t, T, dark=0.28):
    b = ctx.get("bg")
    if b is None: return np.full((H, W, 3), 16, np.uint8)
    k = ctx.get("n", id(b))
    if k not in _BG: _BG.clear(); _BG[k] = cv2.GaussianBlur(b, (0, 0), 18)
    fr = view(_BG[k], 0.5+0.04*math.sin(t*0.4), 0.5, 1.12+0.05*t/max(T, 1))
    return (fr*dark).astype(np.uint8)

def _title(d, txt, t):
    if not txt: return
    a = int(255*ease(t/0.4)); d.text((W/2, 120), txt, font=f(TYPE, 48), fill=IVORY+(a,), anchor="mm")
    w = f(TYPE, 48).getlength(txt); d.line([(W/2-w/2, 160), (W/2-w/2+w*eout((t-0.2)/0.6), 160)], fill=RED+(a,), width=4)

def _fin(fr, layer, p, t):
    if p.get("source"): source_line(layer, "SOURCE: "+p["source"], min(1.0, t/0.5))
    return fr, layer

# ---------- bars: horizontale Balken, wachsen nacheinander, Werte zählen hoch ----------
def bars(t, T, p, ctx):
    fr = bg(ctx, t, T); layer = empty(); d = ImageDraw.Draw(layer); _title(d, p.get("title", ""), t)
    items = p["items"]; n = len(items); vmax = max(v for _, v, *_ in items)
    top = 300 if n <= 3 else 250; gap = min(190, 560//n); bh = int(gap*0.55); x0, x1 = 560, 1440
    for i, it in enumerate(items):
        lab, v, txt = it[0], it[1], (it[2] if len(it) > 2 else str(v))
        t0 = 0.5+0.45*i; pr = eout((t-t0)/1.1)
        if t < t0-0.2: continue
        a = int(255*ease((t-t0+0.2)/0.3)); y = top+i*gap
        hl = p.get("hl") == i; col = GOLD if hl else (IVORY if p.get("hl") is None else (120, 115, 105))
        if it[3:] and it[3] == "red": col = RED
        d.text((x0-30, y+bh/2), lab, font=f(ANTON, 64 if n <= 4 else 52), fill=IVORY+(a,), anchor="rm")
        wbar = (x1-x0)*v/vmax*pr
        d.rectangle([x0, y, x0+wbar, y+bh], fill=col+(min(a, 235),))
        d.rectangle([x0, y+bh-6, x0+wbar, y+bh], fill=(0, 0, 0, 60))
        if pr > 0.05:
            d.text((x0+wbar+24, y+bh/2), txt, font=f(ANTON, 70 if n <= 4 else 56), fill=col+(a,), anchor="lm")
    if p.get("note") and t > 0.6+0.45*n+0.6:
        a = int(255*ease((t-(0.6+0.45*n+0.6))/0.4)); d.text((W/2, H-170), p["note"], font=f(TYPE, 40), fill=IVORY+(a,), anchor="mm")
    return _fin(fr, layer, p, t)

# ---------- breakdown: ein 80-$-Balken teilt sich auf ----------
def breakdown(t, T, p, ctx):
    fr = bg(ctx, t, T); layer = empty(); d = ImageDraw.Draw(layer)
    tot = p.get("total", 80); parts = p["parts"]; x0, x1, y0, y1 = 260, 1660, 430, 610
    d.text((W/2, 250), f"${tot}", font=f(ANTON, 170), fill=IVORY+(int(255*ease(t/0.4)),), anchor="mm")
    grow = eout((t-0.3)/0.8); d.rectangle([x0, y0, x0+(x1-x0)*grow, y1], fill=(60, 56, 50, 255))
    sp = eout((t-1.3)/0.7); cols = [TEAL, GOLD, GREEN, RED]; x = x0; gapw = 24*sp
    for i, (lab, v, pct) in enumerate(parts):
        w = (x1-x0-gapw*(len(parts)-1))*v/tot
        hl = p.get("hl"); dim = hl is not None and hl != i
        col = tuple(int(c*(0.35 if dim else 1)) for c in cols[i % 4])
        if sp > 0:
            lift = -18*eout((t-2.2)/0.4) if hl == i else 0
            d.rectangle([x, y0+lift, x+w*grow, y1+lift], fill=col+(int(255*sp),))
            a = int(255*ease((t-1.6-0.3*i)/0.4))
            if a > 0:
                d.text((x+w/2, y0+lift+(y1-y0)/2), f"${v}", font=f(ANTON, 96), fill=(20, 18, 16, a), anchor="mm")
                d.text((x+w/2, y1+70), lab, font=f(ANTON, 58), fill=(col if not dim else (120, 115, 105))+(a,), anchor="mm")
                d.text((x+w/2, y1+130), pct, font=f(TYPE, 40), fill=IVORY+(int(a*(0.5 if dim else 1)),), anchor="mm")
        x += w+gapw
    if p.get("note") and t > 2.6:
        a = int(255*ease((t-2.6)/0.4)); d.text((W/2, H-150), p["note"], font=f(TYPE, 38), fill=IVORY+(a,), anchor="mm")
    return _fin(fr, layer, p, t)

# ---------- timeline: Linie läuft, Termine werden durchgestrichen ----------
def timeline(t, T, p, ctx):
    fr = bg(ctx, t, T); layer = empty(); d = ImageDraw.Draw(layer); _title(d, p.get("title", ""), t)
    st = p["steps"]; n = len(st); xs = [300+i*(1320/(n-1)) for i in range(n)]; y = 560
    ln = eout((t-0.3)/(0.9*n)); d.line([(xs[0], y), (xs[0]+(xs[-1]-xs[0])*ln, y)], fill=IVORY+(220,), width=6)
    for i, (date, lab, kind) in enumerate(st):
        t0 = 0.4+0.9*i
        if t < t0: continue
        a = int(255*ease((t-t0)/0.3)); ok = kind == "ok"; col = GOLD if ok else IVORY
        r = 22+10*(1-eout((t-t0)/0.3)); d.ellipse([xs[i]-r, y-r, xs[i]+r, y+r], fill=col+(a,))
        d.text((xs[i], y-90), date, font=f(ANTON, 76 if ok else 64), fill=col+(a,), anchor="mm")
        d.text((xs[i], y+80), lab, font=f(TYPE, 40), fill=IVORY+(a,), anchor="mm")
        if not ok:
            pr = eout((t-t0-0.45)/0.3); w = f(ANTON, 64).getlength(date)/2+16
            if pr > 0: d.line([(xs[i]-w, y-90), (xs[i]-w+2*w*pr, y-90)], fill=RED+(255,), width=10)
        else:
            s = 1+0.25*(1-eout((t-t0-0.3)/0.3))
            if t > t0+0.3: d.text((xs[i], y+160), p.get("final", "LAUNCH"), font=f(ANTON, int(64*s)), fill=RED+(255,), anchor="mm")
    return _fin(fr, layer, p, t)

# ---------- flow: Geldfluss Käufer -> Store -> Plattform / Publisher, Münzen wandern ----------
def flow(t, T, p, ctx):
    fr = bg(ctx, t, T); layer = empty(); d = ImageDraw.Draw(layer)
    nodes = p["nodes"]; labs = p.get("labels", ["", "", ""])
    P = [(330, 540), (960, 540), (1590, 330), (1590, 760)]
    def box(i, a):
        x, y = P[i]; txt = nodes[i]; w = max(260, f(ANTON, 54).getlength(txt)+70)
        d.rounded_rectangle([x-w/2, y-70, x+w/2, y+70], 18, fill=(28, 26, 24, a), outline=(GOLD if i == 1 else IVORY)+(a,), width=4)
        d.text((x, y), txt, font=f(ANTON, 54), fill=IVORY+(a,), anchor="mm")
    edges = [(0, 1, 0.9), (1, 2, 2.0), (1, 3, 2.6)]
    for i, t0 in enumerate([0.2, 0.7, 1.7, 2.3]):
        if t > t0: box(i, int(255*ease((t-t0)/0.3)))
    for k, (a_, b_, t0) in enumerate(edges):
        if t < t0: continue
        (xa, ya), (xb, yb) = P[a_], P[b_]; xa += 160 if a_ == 0 else 150; xb -= 170
        pr = eout((t-t0)/0.5); xe, ye = xa+(xb-xa)*pr, ya+(yb-ya)*pr
        d.line([(xa, ya), (xe, ye)], fill=GOLD+(230,), width=6)
        if labs[k] and pr > 0.6:
            d.text(((xa+xb)/2, (ya+yb)/2-50), labs[k], font=f(ANTON, 60), fill=GOLD+(255,), anchor="mm", stroke_width=4, stroke_fill=(0, 0, 0, 255))
        if pr >= 1:   # wandernde Münzen
            for j in range(4):
                u = ((t-t0)*0.8+j/4) % 1; cx, cy = xa+(xb-xa)*u, ya+(yb-ya)*u
                d.ellipse([cx-13, cy-13, cx+13, cy+13], fill=(240, 200, 90, 255), outline=(150, 110, 30, 255), width=3)
    return _fin(fr, layer, p, t)

RENDER = {"bars": bars, "breakdown": breakdown, "timeline": timeline, "flow": flow}
DUR = {"bars": 5.5, "breakdown": 5.5, "timeline": 5.0, "flow": 5.5}
# Laurin 17.11.: Diagramme mit paper_slide (Laurins Paper-Slide-Sound) statt zip; bars: ein Slide je Balken (SOUNDFN unten)
SOUNDS = {"breakdown": [(0.3, "paper_slide", 0.5), (1.3, "money_clink", 0.55)],
          "timeline": [(0.4, "pin", 0.5), (1.3, "pin", 0.5), (2.2, "pin", 0.5)],
          "flow": [(0.9, "paper_slide", 0.5), (2.0, "money_clink", 0.5), (2.6, "paper_slide", 0.45)],
          "phone": [(0.9, "phone_notify", 0.55)]}  # Laurins Notification-Sound (17.11.)
# Laurin 17.11.: die neuen UI-Sounds (ui_blip, whoosh_soft …) klangen schlecht -> verworfen. Diagramme seit 17.11. nachmittags mit paper_slide (Laurin).

# =====================================================================================
# Neue Effekte (Laurin 17.11.2026: mehr Effekte). Alle kostenlos, prozedural.
# FREIGEGEBEN (Laurin 17.11.): phone, calendar, desktop. NICHT freigegeben (nur auf Wunsch): kinetic, ticker.
# ["kinetic", anchor, {"text": "THEY TAKE 30% OF EVERY SALE", "hl": ["30%"]}]          Wort für Wort, Schlüsselwort gold
# ["phone", anchor, {"app": "MARKETS", "title": "Take-Two shares fall 8%", "body": "...", "time": "NOV 9"}]  Push-Nachricht auf Handy
# ["calendar", anchor, {"pages": ["2025", "MAY 26, 2026", "NOV 19, 2026"], "last": "LAUNCH"}]   Abreißkalender blättert
# ["ticker", anchor, {"items": [["TTWO", "-18%"], ["SONY", "+2%"]], "headline": "NET BOOKINGS FELL 18%"}]  Börsen-Laufband
# =====================================================================================
def kinetic(t, T, p, ctx):
    fr = bg(ctx, t, T, 0.22); layer = empty(); d = ImageDraw.Draw(layer)
    words = p["text"].split(); hl = set(w.upper() for w in p.get("hl", []))
    size = 170 if len(words) <= 4 else (140 if len(words) <= 8 else 112); ft = f(ANTON, size)
    # Zeilen umbrechen
    lines, cur = [], []
    for w in words:
        if cur and ft.getlength(" ".join(cur+[w])) > 1650: lines.append(cur); cur = []
        cur.append(w)
    lines.append(cur)
    y0 = H/2 - len(lines)*size*0.62; k = 0
    for li, ln in enumerate(lines):
        x = W/2 - ft.getlength(" ".join(ln))/2; y = y0 + li*size*1.18
        for w in ln:
            t0 = 0.15 + k*p.get("speed", 0.17); k += 1
            if t >= t0:
                e = eout((t-t0)/0.22); a = int(255*e); key = w.upper().strip(".,!?") in hl or w.upper() in hl
                col = GOLD if key else IVORY; dy = 30*(1-e)
                sz = int(size*(1.0+0.25*(1-e))) if key else size
                d.text((x, y+dy), w, font=f(ANTON, sz), fill=col+(a,), stroke_width=4, stroke_fill=(0, 0, 0, a))
                if key and t > t0+0.25:
                    wl = ft.getlength(w); pr = eout((t-t0-0.25)/0.35)
                    d.rectangle([x, y+size*1.08, x+wl*pr, y+size*1.08+8], fill=RED+(255,))
            x += ft.getlength(w+" ")
    return fr, layer

def phone(t, T, p, ctx):
    fr = bg(ctx, t, T, 0.3); layer = empty(); d = ImageDraw.Draw(layer)
    pw, ph = 520, 1000; up = eout(t/0.6); x0 = W/2-pw/2; y0 = 60 + (1-up)*700
    d.rounded_rectangle([x0, y0, x0+pw, y0+ph], 70, fill=(14, 14, 18, 255), outline=(70, 70, 78, 255), width=10)
    d.rounded_rectangle([x0+22, y0+22, x0+pw-22, y0+ph-22], 52, fill=(26, 30, 44, 255))
    d.rounded_rectangle([W/2-70, y0+40, W/2+70, y0+80], 20, fill=(8, 8, 10, 255))
    d.text((W/2, y0+190), p.get("clock", "9:41"), font=f(INTER, 120), fill=IVORY+(230,), anchor="mm")
    d.text((W/2, y0+280), p.get("time", ""), font=f(INTER, 34), fill=(190, 190, 200, 220), anchor="mm")
    t1 = 0.9
    if t > t1:
        e = eout((t-t1)/0.35); cy = y0+380 - 60*(1-e); a = int(245*e)
        title = p.get("title", ""); body = p.get("body", "")
        def wrap(txt, ft, wmax):
            out, cur = [], ""
            for w in txt.split():
                if ft.getlength((cur+" "+w).strip()) > wmax: out.append(cur); cur = w
                else: cur = (cur+" "+w).strip()
            return out+[cur] if cur else out
        tl = wrap(title, f(INTER, 34), pw-130)[:3]; bl = wrap(body, f(INTER, 28), pw-130)[:2]
        bh = max(230, 92+42*len(tl)+36*len(bl)+26)   # Box wächst mit dem Text (17.11.: Text lief unten raus)
        d.rounded_rectangle([x0+40, cy, x0+pw-40, cy+bh], 34, fill=(236, 236, 240, a))
        d.rounded_rectangle([x0+66, cy+26, x0+116, cy+76], 12, fill=RED+(a,))
        d.text((x0+132, cy+36), p.get("app", "NEWS"), font=f(INTER, 28), fill=(90, 90, 96, a))
        d.text((x0+pw-66, cy+36), "now", font=f(INTER, 26), fill=(120, 120, 126, a), anchor="ra")
        yy = cy+92
        for ln in tl: d.text((x0+66, yy), ln, font=f(INTER, 34), fill=(20, 20, 24, a)); yy += 42
        for ln in bl: d.text((x0+66, yy), ln, font=f(INTER, 28), fill=(70, 70, 76, a)); yy += 36
    return fr, layer

def calendar(t, T, p, ctx):
    fr = bg(ctx, t, T, 0.25); layer = empty(); d = ImageDraw.Draw(layer)
    pages = p["pages"]; per = p.get("per", 0.9); cw, chh = 760, 560; x0, y0 = W/2-cw/2, H/2-chh/2+20
    i = min(len(pages)-1, int(max(0, t-0.3)/per)); u = (max(0, t-0.3) % per)/per if i < len(pages)-1 else 0
    def page(txt, sub, a=255, lift=0.0, rot=0):
        pg = Image.new("RGBA", (cw, chh), (0, 0, 0, 0)); g = ImageDraw.Draw(pg)
        g.rounded_rectangle([0, 0, cw, chh], 22, fill=(242, 236, 222, a))
        g.rectangle([0, 0, cw, 120], fill=RED+(a,))
        g.text((cw/2, 60), sub, font=f(ANTON, 60), fill=IVORY+(a,), anchor="mm")
        sz = 150 if len(txt) <= 6 else (110 if len(txt) <= 10 else 90)
        g.text((cw/2, 330), txt, font=f(ANTON, sz), fill=(30, 26, 22, a), anchor="mm")
        for k in range(6): g.ellipse([90+k*110, 14, 110+k*110, 34], fill=(60, 50, 40, a))
        if rot: pg = pg.rotate(rot, expand=True, resample=Image.BICUBIC)
        layer.alpha_composite(pg, (int(W/2-pg.width/2), int(y0+chh/2-pg.height/2-lift)))
    last = i == len(pages)-1
    sub = p.get("last", "") if last else p.get("sub", "")
    if not last and i+1 < len(pages): page(pages[i+1], p.get("last", "") if i+1 == len(pages)-1 else p.get("sub", ""))
    if not last and u > 0.55:
        v = (u-0.55)/0.45; page(pages[i], p.get("sub", ""), int(255*(1-v)), lift=500*v*v, rot=-25*v)
    else: page(pages[i], sub)
    if last and p.get("stamp") and t > 0.3+per*(len(pages)-1)+0.3:
        d.text((W/2+260, y0+chh-40), p["stamp"], font=f(ANTON, 90), fill=RED+(255,), anchor="mm", stroke_width=3, stroke_fill=(0, 0, 0, 255))
    return fr, layer

def ticker(t, T, p, ctx):
    b = ctx.get("bg"); fr = (view(b, 0.5, 0.5, 1.08+0.04*t/max(T, 1))*0.55).astype(np.uint8) if b is not None else np.full((H, W, 3), 14, np.uint8)
    layer = empty(); d = ImageDraw.Draw(layer)
    d.rectangle([0, H-150, W, H-70], fill=(10, 12, 16, 235)); d.rectangle([0, H-150, 260, H-70], fill=RED+(255,))
    d.text((130, H-110), p.get("label", "MARKETS"), font=f(ANTON, 44), fill=IVORY+(255,), anchor="mm")
    items = p["items"]; seg = []
    for sym, val in items: seg += [(sym+"  ", IVORY), (val, (220, 60, 60) if val.startswith("-") else (70, 200, 110)), ("   •   ", (120, 120, 120))]
    ft = f(ANTON, 44); total = sum(ft.getlength(s) for s, _ in seg); x = 280 - (t*220) % total
    while x < W:
        for s, c in seg:
            if x > 260: d.text((x, H-110), s, font=ft, fill=c+(255,), anchor="lm")
            x += ft.getlength(s)
    if p.get("headline") and t > 0.4:
        e = eout((t-0.4)/0.4); a = int(255*e)
        hl = p["headline"]; sz = 110 if len(hl) < 20 else 84
        d.text((W/2, H/2-40+30*(1-e)), hl, font=f(ANTON, sz), fill=IVORY+(a,), anchor="mm", stroke_width=5, stroke_fill=(0, 0, 0, a))
    return fr, layer

RENDER.update({"kinetic": kinetic, "phone": phone, "calendar": calendar, "ticker": ticker})
DUR.update({"kinetic": 4.5, "phone": 5.0, "calendar": 5.0, "ticker": 5.0})

def _calendar_snd(p, dur):
    n = len(p["pages"]); per = p.get("per", 0.9)
    return [(0.3+per*i+0.55*per, "page_turn", 0.65) for i in range(n-1)]
SOUNDFN = {"calendar": _calendar_snd}
SOUNDFN["bars"] = lambda p, dur: [(0.5+0.45*i, "paper_slide", 0.5) for i in range(len(p["items"]))]
DATA = ()   # Musik-Ducking bei Daten-Grafiken: vorerst aus (Laurin 17.11.)

# ---------- desktop: Ermittler-PC, Mauszeiger klickt eine Fallakte an, Fenster öffnet sich (Laurin 17.11.) ---------- [von Laurin freigegeben 17.11.]
#  ["desktop", anchor, {"files": ["Q3_EARNINGS.pdf", "CASE_0047", "LEAKS_2022"], "open": 1,
#                       "title": "CASE_0047", "lines": ["SUBJECT: ROCKSTAR", "BUDGET: $2B+"], "stamp": "CONFIDENTIAL"}]
#  Fensterinhalt = scharfes Szenenbild links + getippte Zeilen rechts. Sound: Mausklick beim Anklicken (mouse_click).
DESK_T = {"sel": 1.35, "dbl": 1.75, "open": 1.95}
def _folder(d, x, y, s, a, sel):
    if sel: d.rounded_rectangle([x-18, y-14, x+s+18, y+s*0.82+70], 10, fill=(70, 120, 200, int(90*a/255)), outline=(120, 170, 240, int(200*a/255)), width=2)
    d.polygon([(x, y+10), (x+s*0.38, y+10), (x+s*0.46, y+24), (x+s, y+24), (x+s, y+s*0.78), (x, y+s*0.78)], fill=(176, 138, 70, a))
    d.rectangle([x, y+34, x+s, y+s*0.78], fill=(214, 172, 96, a))
    d.line([(x, y+34), (x+s, y+34)], fill=(236, 200, 128, a), width=3)

def _cursor(layer, x, y, press):
    s = 1.0-0.12*press
    pts = [(0, 0), (0, 40), (10, 31), (17, 47), (24, 44), (17, 29), (30, 29)]
    pts = [(x+px*s*1.3, y+py*s*1.3) for px, py in pts]
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(sh).polygon([(px+4, py+5) for px, py in pts], fill=(0, 0, 0, 150))
    layer.alpha_composite(sh.filter(ImageFilter.GaussianBlur(3)))
    ImageDraw.Draw(layer).polygon(pts, fill=(250, 250, 250, 255), outline=(10, 10, 10, 255))

def desktop(t, T, p, ctx):
    fr = (np.asarray(bg(ctx, t, T, 0.18), np.float32)*np.array([0.8, 0.9, 1.1])).clip(0, 255).astype(np.uint8)
    layer = empty(); d = ImageDraw.Draw(layer)
    files = p.get("files", ["CASE_FILE"]); k = min(p.get("open", 0), len(files)-1)
    a0 = int(255*ease(t/0.35))
    # Bildschirm: Monitor-Rahmen + Taskleiste
    d.rounded_rectangle([60, 50, W-60, H-50], 26, outline=(40, 40, 46, a0), width=14)
    d.rectangle([74, 64, W-74, 112], fill=(18, 20, 26, int(a0*0.95)))
    d.text((104, 88), p.get("os", "EVIDENCE TERMINAL"), font=f(INTER, 26), fill=(170, 175, 185, a0), anchor="lm")
    d.text((W-104, 88), p.get("clock", "02:14 AM"), font=f(INTER, 26), fill=(170, 175, 185, a0), anchor="rm")
    # Ordner-Raster
    s = 150; gap = 330; n = len(files); x0 = W/2-(n-1)*gap/2; y0 = 380
    pos = []
    for i, name in enumerate(files):
        ai = int(a0*ease((t-0.15-0.12*i)/0.3)); x = x0+i*gap-s/2
        sel = i == k and t >= DESK_T["sel"]
        _folder(d, x, y0, s, ai, sel)
        lbl = name if f(INTER, 26).getlength(name) < 280 else name[:16]+"…"
        d.text((x+s/2, y0+s*0.78+30), lbl, font=f(INTER, 26), fill=(235, 235, 240, ai), anchor="mm")
        pos.append((x+s/2, y0+s*0.45))
    # Zeiger fährt zur Akte
    tx, ty = pos[k]; sx, sy = W*0.82, H*0.86
    m = ease((t-0.45)/0.85); cx = sx+(tx-sx)*m + 40*math.sin(m*math.pi)*(1-m); cy = sy+(ty-sy)*m
    press = max(0, 1-abs(t-DESK_T["sel"])/0.06) + max(0, 1-abs(t-DESK_T["dbl"])/0.05) + max(0, 1-abs(t-DESK_T["dbl"]-0.12)/0.05)
    # Fenster öffnet sich aus der Akte heraus
    to = DESK_T["open"]
    if t >= to:
        e = eout((t-to)/0.35); ww, wh = 1500, 760; wx, wy = W/2, H/2+40
        cw, ch = ww*(0.15+0.85*e), wh*(0.15+0.85*e); X0 = tx+(wx-tx)*e-cw/2; Y0 = ty+(wy-ty)*e-ch/2
        win = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dw = ImageDraw.Draw(win)
        dw.rectangle([X0+14, Y0+18, X0+cw+14, Y0+ch+18], fill=(0, 0, 0, 150))
        win = win.filter(ImageFilter.GaussianBlur(14)); dw = ImageDraw.Draw(win)
        dw.rectangle([X0, Y0, X0+cw, Y0+ch], fill=(232, 226, 212, 255))
        dw.rectangle([X0, Y0, X0+cw, Y0+54*e+1], fill=(30, 33, 42, 255))
        if e > 0.9:
            dw.text((X0+28, Y0+27), p.get("title", files[k]), font=f(INTER, 26), fill=(220, 220, 228, 255), anchor="lm")
            for j, c in enumerate([(205, 60, 60), (220, 170, 60), (80, 170, 90)]):
                dw.ellipse([X0+cw-40-j*34-11, Y0+16, X0+cw-40-j*34+11, Y0+38], fill=c+(255,))
            b = ctx.get("bg")
            if b is not None:
                ih = int(wh-124); iw = int(ih*b.shape[1]/b.shape[0]); im = Image.fromarray(b).resize((iw, ih))
                im = im.crop(((iw-700)//2, 0, (iw-700)//2+700, ih))
                win.alpha_composite(im.convert("RGBA"), (int(X0+40), int(Y0+84)))
            tx0 = X0+(780 if b is not None else 60); yy = Y0+110; tt = t-to-0.45
            chars = int(max(0, tt)*38)
            for ln in p.get("lines", []):
                shown = ln[:max(0, chars)]; chars -= len(ln)+4
                dw.text((tx0, yy), shown, font=f(TYPE, 40), fill=(28, 22, 18, 255)); yy += 70
            if p.get("stamp") and t > to+1.6:
                q = eout((t-to-1.6)/0.18); sz = int(64*(1.6-0.6*q))
                st = Image.new("RGBA", (900, 200), (0, 0, 0, 0)); ds = ImageDraw.Draw(st)
                ds.rectangle([10, 10, 890, 190], outline=RED+(int(230*q),), width=8)
                ds.text((450, 100), p["stamp"], font=f(ANTON, sz), fill=RED+(int(230*q),), anchor="mm")
                st = st.rotate(-8, expand=True, resample=Image.BICUBIC)
                win.alpha_composite(st, (int(X0+cw-st.width-30), int(Y0+ch-st.height-20)))
        layer.alpha_composite(win)
    if t < to+0.5: _cursor(layer, cx, cy, min(1, press))
    return fr, layer

def _desktop_snd(p, dur):
    ev = [(DESK_T["sel"], "mouse_click", 0.7), (DESK_T["dbl"], "mouse_click", 0.6), (DESK_T["dbl"]+0.12, "mouse_click", 0.65)]
    if p.get("stamp"): ev.append((DESK_T["open"]+1.6, "slap", 0.5))
    import random; random.seed(7); t0 = DESK_T["open"]+0.45; k = 0   # Tastatur wie beim Schreibmaschinentext (38 Zeichen/s)
    for ln in p.get("lines", []):
        for ch in ln:
            if ch != " " and k % 2 == 0: ev.append((t0+k/38, f"key{random.randint(0,3)}", 0.75*0.6))
            k += 1
        k += 4
    return ev
RENDER["desktop"] = desktop; DUR["desktop"] = 5.5; SOUNDFN["desktop"] = _desktop_snd
