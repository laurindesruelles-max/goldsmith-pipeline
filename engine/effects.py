"""Vollbild-Effekte für part2.py (spec-Kinds). Jeder Effekt: render(t, T, params, ctx) -> (frame_rgb, layer_rgba).
Kinds in spec.json (Anker = Startzeitpunkt, Dauer standardmäßig 4.5 s):
  ["doc", anchor, {"title": "CONFIDENTIAL — INTERNAL MEMO", "lines": [...], "hl": [3, 4]}]      Dokument-Zoom + Textmarker
  ["redact", anchor, {"top": "FILE NO. 001 — OWNER OF RECORD", "name": "LUXOTTICA", "bottom": "ITALY · 1961"}]   Schwärzung aufdecken
  ["chart", anchor, {"title": "OAKLEY SHARE PRICE · 1996", "dir": "down", "value": "-33%"}]      animiertes Diagramm
  ["route", anchor, {"points": [["FACTORY", 0.27, 0.6], ...], "map": "worldmap.png"}]   Landkarte mit Routen (Punkte in Bildschirm-Anteilen; map optional aus img/)
  ["split", anchor, {"left_img": 18, "right_img": 19, "left": "BEFORE", "right": "AFTER", "left_sub": "...", "right_sub": "..."}]
  ["news", anchor, {"date": "JUNE 2007", "h1": "EYEWEAR GIANT", "h2": "SWALLOWS RIVAL", "sub": "...", "stamp": "BREAKING"}]
  ["parallax", anchor, {}]   braucht img/N_fg.png (Higgsfield remove_background des Szenenbilds)
  ["photo", anchor, {"file": "real_x_1.jpg", "caption": ["NAME", "JAHR"], "style": "print"|"full"}]   echtes Foto (engine/sources.py),
      Bildnachweis automatisch aus img/credits.json unten links
  doc/news/chart: optional "source": "SEC FORM 20-F, 2018" / "REUTERS, 12 JUL 2018" -> Quellenzeile unten links.
      news = nur kurzes Zitat (Überschrift) im EIGENEN Layout, nie Logo/Screenshot des Mediums.
Übergänge (Film Burn / Glitch / Paper Wipe) wechseln automatisch an Schnitten (transition()).
Fakten in doc/news/chart müssen belegt sein (Quellen im Skript)!
"""
import os, math, random, numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter
W, H = 1920, 1080
F = os.path.expanduser("~/.fonts")
ANTON = f"{F}/Anton.ttf"; TYPE = f"{F}/SpecialElite.ttf"; SERIF = f"{F}/playfair-display-latin-700-normal.ttf"; SERIF4 = f"{F}/playfair-display-latin-400-normal.ttf"
INTER = "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf"
GOLD = (222, 188, 104); IVORY = (242, 234, 216); RED = (205, 25, 35); INK = (28, 22, 18)
DUR = {"doc": 4.5, "redact": 4.0, "chart": 4.5, "route": 4.5, "split": 4.5, "news": 4.0, "parallax": 5.0}
_FC = {}
def f(p, s):
    k = (p, int(s))
    if k not in _FC: _FC[k] = ImageFont.truetype(p, int(s))
    return _FC[k]
def ease(s): s = min(max(s, 0), 1); return s*s*(3-2*s)
def eout(s): s = min(max(s, 0), 1); return 1-(1-s)**3
def empty(): return Image.new("RGBA", (W, H), (0, 0, 0, 0))
def load(p, w=W, h=H):
    im = Image.open(p).convert("RGB"); s = max(w/im.width, h/im.height); im = im.resize((int(im.width*s)+1, int(im.height*s)+1), Image.LANCZOS)
    x, y = (im.width-w)//2, (im.height-h)//2; return np.asarray(im.crop((x, y, x+w, y+h)))
def view(img, cx, cy, z, rot=0):
    ih, iw = img.shape[:2]; cw = iw/z; ch = cw*H/W
    x0 = min(max(cx*iw-cw/2, 0), iw-cw); y0 = min(max(cy*ih-ch/2, 0), ih-ch); sc = W/cw
    M = np.float32([[sc, 0, -x0*sc], [0, sc, -y0*sc]])
    if rot:
        R = cv2.getRotationMatrix2D((W/2, H/2), rot, 1.0); M = (np.vstack([R, [0, 0, 1]]) @ np.vstack([M, [0, 0, 1]]))[:2].astype(np.float32)
    return cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
_PAPER = {}
def paper(w, h, seed=1, tint=(234, 225, 200)):
    k = (w, h, seed, tint)
    if k not in _PAPER:
        rng = np.random.default_rng(seed); a = np.full((h, w, 3), tint, np.float32)
        a += rng.normal(0, 6, (h, w, 1)); a *= (1-0.24*cv2.GaussianBlur(rng.random((h, w)).astype(np.float32), (0, 0), 40)[..., None])
        _PAPER[k] = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")
    return _PAPER[k].copy()
_CACHE = {}

# ---------- doc: Dokument-Zoom + Textmarker ----------
def doc(t, T, p, ctx):
    key = ("doc", id(p))
    if key not in _CACHE:
        d0 = paper(1100, 1400, 3); d = ImageDraw.Draw(d0)
        d.text((80, 70), p.get("title", "CONFIDENTIAL  —  INTERNAL MEMO"), font=f(TYPE, 40), fill=(150, 30, 30)); d.line([(80, 130), (1020, 130)], fill=INK, width=3)
        for i, ln in enumerate(p["lines"][:14]): d.text((80, 190+i*72), ln, font=f(TYPE, 46), fill=INK)
        desk = Image.fromarray(load(ctx["a"]+"/desk.png", int(W*1.2), int(H*1.2))).convert("RGBA")
        dr = d0.rotate(-3, expand=True, resample=Image.BICUBIC)
        sh = Image.new("RGBA", desk.size, (0, 0, 0, 0)); ImageDraw.Draw(sh).rectangle([620, 120, 620+dr.width-40, 120+dr.height-40], fill=(0, 0, 0, 160))
        desk.alpha_composite(sh.filter(ImageFilter.GaussianBlur(25))); desk.alpha_composite(dr, (580, 70)); _CACHE[key] = desk
    base = _CACHE[key].copy(); hl = Image.new("RGBA", base.size, (0, 0, 0, 0)); dh = ImageDraw.Draw(hl)
    lines = p["lines"]
    for j, li in enumerate(p.get("hl", [])):
        pr = eout((t-1.6-0.6*j)/0.45)
        if pr > 0 and li < len(lines):
            w = f(TYPE, 46).getlength(lines[li]); y = 70+190+li*72+8+li*2; dh.rectangle([660, y, 660+(w+30)*pr, y+52], fill=(255, 230, 40, 120))
    base.alpha_composite(hl)
    li0 = p.get("hl", [3])[0] if p.get("hl") else 3; cy = min(0.75, max(0.3, (70+190+li0*72)/base.height))
    z = 1.0+1.0*ease(t/1.5); cyy = 0.45+(cy-0.45)*ease(t/1.5)
    return view(np.asarray(base.convert("RGB")), 0.56, cyy, z, rot=-1.5*ease(t/1.5)), empty()

# ---------- redact: Schwärzung aufdecken ----------
def redact(t, T, p, ctx):
    fr = np.asarray(paper(W, H, 5).convert("RGB")); layer = empty(); d = ImageDraw.Draw(layer)
    d.text((W/2, 260), p.get("top", ""), font=f(TYPE, 52), fill=INK, anchor="mm")
    nm = p["name"]; size = 230 if len(nm) < 11 else int(230*11/len(nm))
    d.text((W/2, 520), nm, font=f(ANTON, size), fill=(150, 20, 28), anchor="mm")
    d.text((W/2, 760), p.get("bottom", ""), font=f(TYPE, 52), fill=INK, anchor="mm")
    for i, (y0, y1, t0) in enumerate([(220, 300, 0.8), (390, 650, 1.4), (720, 800, 2.2)]):
        pr = eout((t-t0)/0.35); x = -W*pr*(1 if i % 2 == 0 else -1)
        if pr < 1: d.rectangle([260+x, y0, W-260+x, y1], fill=(10, 10, 10, 255))
    return view(fr, 0.5, 0.5, 1.0+0.06*ease(t/T)), layer

# ---------- chart: animiertes Diagramm ----------
def chart(t, T, p, ctx):
    fr = np.asarray(paper(W, H, 7, (238, 236, 228)).convert("RGB")); layer = empty(); d = ImageDraw.Draw(layer)
    for x in range(200, 1760, 80): d.line([(x, 220), (x, 900)], fill=(170, 190, 210, 120), width=1)
    for y in range(220, 901, 68): d.line([(200, y), (1720, y)], fill=(170, 190, 210, 120), width=1)
    d.text((200, 140), p.get("title", ""), font=f(TYPE, 46), fill=INK)
    down = p.get("dir", "down") == "down"; rng = random.Random(4); pts = []; v = 0.75 if down else 0.25
    for i in range(60):
        if down: v += rng.uniform(-0.02, 0.025) if i < 30 else rng.uniform(-0.045, 0.012)
        else: v += rng.uniform(-0.025, 0.02) if i < 30 else rng.uniform(-0.012, 0.045)
        pts.append((200+i*25.5, 220+(1-v)*680))
    col = (200, 20, 30, 255) if (down or p.get("bad")) else (30, 150, 70, 255)
    n = int(len(pts)*eout(t/2.6))
    if n > 1:
        d.line(pts[:n], fill=col, width=8, joint="curve"); x, y = pts[n-1]; d.ellipse([x-12, y-12, x+12, y+12], fill=col)
    if t > 2.7 and p.get("value"):
        a = int(255*ease((t-2.7)/0.25)); s = 1+0.2*(1-eout((t-2.7)/0.3))
        d.text((1450, 560), p["value"], font=f(ANTON, 200*s), fill=col[:3]+(a,), anchor="mm", stroke_width=6, stroke_fill=(255, 255, 255, a))
    return fr, layer

# ---------- route: Landkarte mit Routen ----------
def route(t, T, p, ctx):
    mp = p.get("map"); mpath = f"{ctx['img']}/{mp}" if mp else ctx["a"]+"/map.png"
    if ("map", mpath) not in _CACHE: _CACHE[("map", mpath)] = load(mpath, int(W*1.3), int(H*1.3))
    fr = view(_CACHE[("map", mpath)], 0.5, 0.5, 1.15+0.15*ease(t/T)); layer = empty(); d = ImageDraw.Draw(layer)
    P = [(lab, x*W, y*H, 0.3+i*1.0) for i, (lab, x, y) in enumerate(p["points"][:5])]
    for i, (lab, x, y, t0) in enumerate(P):
        if i > 0:
            _, px, py, _ = P[i-1]; pr = eout((t-(t0-0.9))/0.8); segs = 28
            def bz(u, px=px, py=py, x=x, y=y):
                mx, my = (px+x)/2, min(py, y)-160; return ((1-u)**2*px+2*(1-u)*u*mx+u*u*x, (1-u)**2*py+2*(1-u)*u*my+u*u*y)
            for s in range(int(segs*pr)):
                if s % 2 == 0: d.line([bz(s/segs), bz((s+1)/segs)], fill=(205, 22, 32, 255), width=9)
        if t >= t0:
            pr = eout((t-t0)/0.25); yy = y-200*(1-pr)
            d.ellipse([x-26, yy-26, x+26, yy+26], fill=(210, 25, 35, 255), outline=(90, 0, 0, 255), width=4)
            if t > t0+0.3:
                vis = lab[:int((t-t0-0.3)*18)]; tw = d.textlength(lab, font=f(TYPE, 44))
                d.rectangle([x-tw/2-20, y+40, x+tw/2+20, y+105], fill=(240, 232, 210, 235)); d.text((x, y+72), vis, font=f(TYPE, 44), fill=INK, anchor="mm")
    return fr, layer

# ---------- split: Vorher / Nachher ----------
def split(t, T, p, ctx):
    key = ("split", p["left_img"], p["right_img"])
    if key not in _CACHE:
        L = load(f"{ctx['img']}/{p['left_img']}.png", 960, 1080); R = load(f"{ctx['img']}/{p['right_img']}.png", 960, 1080)
        g = cv2.cvtColor(L, cv2.COLOR_RGB2GRAY); _CACHE[key] = (cv2.cvtColor(g, cv2.COLOR_GRAY2RGB), R)
    L, R = _CACHE[key]; pr = eout((t-0.2)/0.6); fr = np.zeros((H, W, 3), np.uint8); fr[:, :W//2] = (L*0.85).astype(np.uint8)
    wv = int(960*pr); fr[:, W//2:W//2+wv] = R[:, :wv]
    layer = empty(); d = ImageDraw.Draw(layer); d.rectangle([W//2-4, 0, W//2+4, H], fill=(240, 240, 240, 255))
    for x, txt, col, t0 in [(W//4, p.get("left", "BEFORE"), (255, 255, 255), 0.5), (3*W//4, p.get("right", "AFTER"), GOLD, 1.1)]:
        if t > t0:
            a = int(255*ease((t-t0)/0.25)); d.text((x, 900), txt, font=f(ANTON, 130), fill=col+(a,), anchor="mm", stroke_width=6, stroke_fill=(0, 0, 0, a))
    for x, txt, t0 in [(W//4, p.get("left_sub", ""), 1.8), (3*W//4, p.get("right_sub", ""), 2.4)]:
        if txt and t > t0: d.text((x, 1000), txt[:int((t-t0)*18)], font=f(TYPE, 46), fill=IVORY, anchor="mm")
    return fr, layer

# ---------- news: Zeitungs-Wirbel ----------
def news(t, T, p, ctx):
    key = ("news", id(p))
    if key not in _CACHE:
        w, h = 1100, 680; c = paper(w, h, 11); d = ImageDraw.Draw(c)
        mast = f"AS REPORTED BY {p['source'].split(',')[0]}" if p.get("source") else "THE FINANCIAL RECORD"   # echtes Zitat: kein erfundenes Blatt
        d.text((50, 35), f"{mast}  ·  {p.get('date', '')}", font=f(INTER, 30), fill=(60, 50, 40)); d.line([(50, 85), (w-50, 85)], fill=INK, width=4)
        d.text((50, 110), p["h1"], font=f(SERIF, 100 if len(p["h1"]) < 16 else 80), fill=INK); d.text((50, 225), p.get("h2", ""), font=f(SERIF, 100 if len(p.get("h2", "")) < 16 else 80), fill=INK)
        d.text((50, 360), p.get("sub", ""), font=f(SERIF4, 42), fill=(55, 45, 38))
        for col in range(3):
            for r in range(9): d.line([(50+col*340, 440+r*24), (50+col*340+300, 440+r*24)], fill=(120, 110, 95), width=8)
        _CACHE[key] = c
    clip = _CACHE[key]; bg = ctx.get("bg")
    fr = (view(bg, 0.5, 0.5, 1.05)*0.45).astype(np.uint8) if bg is not None else np.full((H, W, 3), 18, np.uint8)
    layer = empty(); pr = eout(t/1.3); s = 0.05+0.95*pr; rot = (1-pr)*720+3
    im = clip.resize((max(2, int(clip.width*s)), max(2, int(clip.height*s)))).rotate(rot, expand=True, resample=Image.BICUBIC)
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); sh.alpha_composite(Image.new("RGBA", im.size, (0, 0, 0, 170)), (int(W/2-im.width/2+20), int(H/2-im.height/2+25)))
    layer.alpha_composite(sh.filter(ImageFilter.GaussianBlur(18))); layer.alpha_composite(im, (int(W/2-im.width/2), int(H/2-im.height/2)))
    if t > 2.0 and p.get("stamp"):
        q = eout((t-2.0)/0.12); st = Image.new("RGBA", (760, 260), (0, 0, 0, 0)); sd = ImageDraw.Draw(st)
        sd.rounded_rectangle([10, 10, 750, 250], radius=16, outline=RED, width=14); sd.text((380, 130), p["stamp"], font=f(ANTON, 160 if len(p["stamp"]) < 9 else 120), fill=RED, anchor="mm")
        st = st.rotate(-10, expand=True); sc = 2-q; st = st.resize((int(st.width*sc*0.8), int(st.height*sc*0.8)))
        st.putalpha(st.getchannel("A").point(lambda v: int(v*min(1, q*1.4)*0.92))); layer.alpha_composite(st, (int(W*0.68-st.width/2), int(H*0.72-st.height/2)))
    return fr, layer

# ---------- parallax ----------
def parallax(t, T, p, ctx):
    n = ctx["n"]; fgp = f"{ctx['img']}/{n}_fg.png"; key = ("par", n)
    if key not in _CACHE:
        if not os.path.exists(fgp): _CACHE[key] = None
        else:
            bg = load(f"{ctx['img']}/{n}.png"); fg = np.array(Image.open(fgp).convert("RGBA").resize((W, H)))
            mask = cv2.dilate((fg[..., 3] > 20).astype(np.uint8), np.ones((25, 25)))*255
            sm = cv2.resize(bg, None, fx=0.5, fy=0.5); ms = cv2.resize(mask, None, fx=0.5, fy=0.5)
            inp = cv2.GaussianBlur(cv2.resize(cv2.inpaint(sm, ms, 9, cv2.INPAINT_TELEA), (W, H)), (0, 0), 6)
            _CACHE[key] = (np.where(mask[..., None] > 0, inp, cv2.GaussianBlur(bg, (0, 0), 2.5)), fg, np.random.default_rng(n).random((55, 4)))
    data = _CACHE[key]
    if data is None: return None
    bgl, fg, P = data; e = ease(t/T)
    def place(img, s, dx, dy, border):
        h, w = img.shape[:2]; sc = W/w*s; M = np.float32([[sc, 0, W/2-w*sc/2+dx], [0, sc, H/2-h*sc/2+dy]])
        return cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=border)
    B = place(bgl, 1.10+0.04*e, -40*e, 10*e, cv2.BORDER_REFLECT).astype(np.float32)
    Fg = place(fg, 1.04+0.16*e, -170*e, 40*e, cv2.BORDER_CONSTANT).astype(np.float32)
    al = Fg[..., 3:4]/255; out = B*(1-al)+Fg[..., :3]*al
    dd = np.zeros((H, W), np.float32); k = int(t*30)
    for x, y, r, b in P: cv2.circle(dd, (int((x*W*1.3-300*e*(1+b)) % W), int((y*H+25*math.sin(k/20+x*9)) % H)), int(2+5*r), 1.0, -1)
    dd = cv2.GaussianBlur(dd, (0, 0), 2.5)[..., None]*0.45; out = out*(1-dd)+np.array([255, 215, 160], np.float32)*dd
    return np.clip(out, 0, 255).astype(np.uint8), empty()

# ---------- photo: echtes Archivfoto (engine/sources.py, nur zulässige Lizenzen) ----------
def _credit_for(p, ctx):
    if p.get("credit"): return p["credit"]
    cp = f"{ctx['img']}/credits.json"
    if os.path.exists(cp):
        import json as _j
        for c in _j.load(open(cp)):
            if c["file"] == p["file"]: return c.get("credit") or f"{c['author']} / {c['license']}"
    return ""

def source_line(layer, text, a=1.0):
    """Kleine Quellen-/Bildnachweis-Zeile unten links (Pflicht bei echten Fotos/Zitaten)."""
    if not text: return
    d = ImageDraw.Draw(layer); ft = f(TYPE, 26); tw = d.textlength(text, font=ft)
    d.rectangle([34, H-74, 34+tw+28, H-30], fill=(10, 8, 6, int(150*a))); d.text((48, H-68), text, font=ft, fill=IVORY+(int(230*a),))

def photo(t, T, p, ctx):
    """Echtes Foto als Abzug auf dem Ermittlertisch (style "print", Standard) oder bildfüllend mit Kamerafahrt ("full").
    Unverändert (nur Ausschnitt/Zoom), Bildnachweis unten links, optional getippte Bildunterschrift."""
    key = ("photo", p["file"], p.get("style", "print"))
    if key not in _CACHE:
        im = Image.open(f"{ctx['img']}/{p['file']}").convert("RGB")
        if p.get("style") == "full":
            _CACHE[key] = np.asarray(im.resize((int(W*1.15), int(W*1.15*im.height/im.width)) if im.width/im.height > W/H else (int(H*1.15*im.width/im.height), int(H*1.15)), Image.LANCZOS))
        else:
            desk = Image.fromarray(load(ctx["a"]+"/desk.png", int(W*1.15), int(H*1.15))).convert("RGBA")
            mw, mh = int(desk.width*0.62), int(desk.height*0.7); sc = min(mw/im.width, mh/im.height)
            ph = im.resize((int(im.width*sc), int(im.height*sc)), Image.LANCZOS)
            pr = Image.new("RGBA", (ph.width+40, ph.height+40), (236, 230, 214, 255)); pr.paste(ph, (20, 20)); pr = pr.rotate(-2.0, expand=True, resample=Image.BICUBIC)
            x0, y0 = (desk.width-pr.width)//2, (desk.height-pr.height)//2
            sh = Image.new("RGBA", desk.size, (0, 0, 0, 0)); ImageDraw.Draw(sh).rectangle([x0+25, y0+35, x0+pr.width+25, y0+pr.height+35], fill=(0, 0, 0, 170))
            desk.alpha_composite(sh.filter(ImageFilter.GaussianBlur(22))); desk.alpha_composite(pr, (x0, y0)); _CACHE[key] = np.asarray(desk.convert("RGB"))
    base = _CACHE[key]; e = ease(t/T)
    fr = view(base, 0.5+0.03*e, 0.5-0.02*e, 1.0+0.12*e) if p.get("style") == "full" else view(base, 0.5, 0.5, 1.02+0.1*e, rot=-0.6*e)
    layer = empty(); a = min(1, t/0.3)
    if p.get("caption") and t > 0.6:
        d = ImageDraw.Draw(layer); ft = f(TYPE, 48); y = 120; n = int((t-0.6)*16)
        for ln in p["caption"]:
            vis = ln[:max(0, n)]; n -= len(ln)
            if vis:
                tw = d.textlength(ln, font=ft); d.rectangle([110, y-12, 110+tw+36, y+62], fill=(240, 232, 210, 235)); d.text((128, y), vis, font=ft, fill=INK)
            y += 84
    source_line(layer, _credit_for(p, ctx), a)
    return fr, layer

def _with_source(fn):
    def w(t, T, p, ctx):
        r = fn(t, T, p, ctx)
        if r is None or not p.get("source"): return r
        fr, layer = r; source_line(layer, "SOURCE: " + p["source"]); return fr, layer
    return w

RENDER = {"doc": _with_source(doc), "redact": redact, "chart": _with_source(chart), "route": route, "split": split,
          "news": _with_source(news), "parallax": parallax, "photo": photo}
DUR["photo"] = 5.0

# ---------- endcard: Pflicht-Ende (Kommentar-Feld, Subscribe-Button, wackelnde Glocke) ----------
def endcard(t, T, p, ctx):
    bg = ctx.get("bg")
    fr = (view(bg, 0.5, 0.5, 1.05+0.04*ease(t/T))*0.35).astype(np.uint8) if bg is not None else np.full((H, W, 3), 14, np.uint8)
    layer = empty(); d = ImageDraw.Draw(layer)
    # Kommentar-Feld
    a1 = eout((t-0.2)/0.4)
    if a1 > 0:
        x0, y0 = 360, int(230+40*(1-a1))
        d.rounded_rectangle([x0, y0, W-360, y0+190], radius=22, fill=(245, 242, 235, int(240*a1)))
        d.ellipse([x0+30, y0+45, x0+130, y0+145], fill=(60, 60, 64, int(255*a1)))
        q = p.get("question", "TELL US IN THE COMMENTS")
        n = int(max(0, t-0.6)*22); d.text((x0+170, y0+52), q[:n], font=f(TYPE, 44), fill=INK+(int(255*a1),))
        if n < len(q) and int(t*2) % 2 == 0: pass
        d.line([(x0+170, y0+130), (W-420, y0+130)], fill=(120, 120, 125, int(200*a1)), width=3)
    # Subscribe-Button (generisch, kein Logo)
    a2 = eout((t-1.4)/0.3)
    if a2 > 0:
        bx, by = W//2-330, 560; s2 = 1+0.15*(1-a2)
        pressed = t > 2.6
        col = (60, 60, 64) if pressed else (204, 24, 30)
        bw, bh = int(460*s2), int(120*s2)
        d.rounded_rectangle([bx+230-bw//2, by+60-bh//2, bx+230+bw//2, by+60+bh//2], radius=bh//2, fill=col+(int(255*a2),))
        d.text((bx+230, by+60), "SUBSCRIBED" if pressed else "SUBSCRIBE", font=f(ANTON, int(64*s2)), fill=(255, 255, 255, int(255*a2)), anchor="mm")
    # Glocke (gezeichnet), wackelt
    a3 = eout((t-1.8)/0.3)
    if a3 > 0:
        gx, gy = W//2+260, 620; ang = math.radians(18*math.sin((t-2.9)*14)*math.exp(-max(0, t-2.9)*2.5)) if t > 2.9 else 0
        bell = Image.new("RGBA", (220, 220), (0, 0, 0, 0)); bd = ImageDraw.Draw(bell); c = (255, 255, 255, int(255*a3))
        bd.pieslice([45, 30, 175, 170], 180, 360, fill=c); bd.rectangle([45, 98, 175, 150], fill=c); bd.polygon([(30, 165), (190, 165), (175, 140), (45, 140)], fill=c)
        bd.ellipse([95, 160, 125, 190], fill=c); bd.ellipse([100, 15, 120, 35], fill=c)
        bell = bell.rotate(math.degrees(ang), center=(110, 30), resample=Image.BICUBIC)
        layer.alpha_composite(bell, (gx-110, gy-110))
        if t > 2.9 and int((t-2.9)*6) % 2 == 0 and t < 4.2:
            for k2 in (-1, 1): d.arc([gx-150+k2*0, gy-120, gx+150, gy+120], 300 if k2 > 0 else 200, 340 if k2 > 0 else 240, fill=(222, 188, 104, 220), width=8)
    return fr, layer
RENDER["endcard"] = endcard; DUR["endcard"] = 6.0

# ---------- 3D-Diorama (engine/dio_fx.py): Earth Zoom + Polaroid-Zoom ----------
try:
    import dio_fx as DX
    RENDER.update({"earthzoom": DX.earthzoom, "dio": DX.dio}); DUR.update({"earthzoom": 9.0, "dio": 8.0})
    SOUNDFN = {"earthzoom": DX.earthzoom_sounds, "dio": DX.dio_sounds}
except Exception as _e:   # Blender-Clips/Module fehlen -> Effekte deaktiviert
    print("dio_fx nicht geladen:", _e); SOUNDFN = {}
DUCK = ("earthzoom", "dio")   # Musik in 3D-Szenen leicht absenken (Raumklang hörbar)


def dur_of(kind, params, t0, scene_T):
    """Dauer eines Vollbild-Effekts: params["dur"] (Sekunden oder "scene") sonst Standard."""
    d = params.get("dur") if isinstance(params, dict) else None
    if d == "scene": return max(0.5, scene_T-t0)
    if d: return float(d)
    return DUR[kind]
SOUNDS = {"doc": [(0.05, "paper", 0.5), (1.6, "marker_stroke", 0.8), (2.2, "marker_stroke2", 0.8)],   # Laurins eigener Marker-Sound (17.11.)
          "redact": [(0.78, "paper_slide", 0.55), (1.38, "paper_slide", 0.65), (1.42, "sub_drop", 0.8), (2.18, "paper_slide", 0.55)],   # Laurin 17.11.: Paper-Slide je Balken
          "chart": [(0.15, "data_loading", 0.6), (2.7, "sub_drop", 1.0)],   # Laurin 17.11.: Data-Loading-Sound statt Herzschlag + Ticks
          "route": [(0.3, "pin", 0.8), (1.3, "pin", 0.8), (2.3, "pin", 0.8), (0.5, "zip", 0.4), (1.5, "zip", 0.4)],
          "split": [(0.2, "whoosh", 0.3), (0.5, "slap", 0.6), (1.1, "coins", 0.8)],
          "news": [(0.0, "news_spin", 0.7), (1.25, "flash", 0.9), (2.05, "stamp", 1.0)],   # Laurins Zeitungs-Sound (17.11.)
          "parallax": [(0.1, "whoosh", 0.2)],
          "photo": [(0.0, "paper", 0.45)]}

SOUNDS["endcard"] = [(0.2, "paper_slide", 0.6), (1.45, "slap", 0.5), (2.6, "shutter", 0.6), (2.95, "service_bell", 0.55)]
# ---------- Übergänge an Schnitten ----------
TRANS = ["burn", None, "glitch", None, None, None]   # Laurin 16.11.: kein weißer Wipe-Balken mehr, Übergänge selten   # nicht jeder Schnitt bekommt einen Effekt
TSOUND = {"burn": ("film_projector", 0.6), "glitch": ("glitch", 0.8), "wipe": ("paper_tear", 0.6)}
def trans_kind(n, i): return TRANS[(n*7+i*3) % len(TRANS)]
def transition(fr, prev, kind, lt, seed=0):
    out = fr.astype(np.float32)
    if kind == "burn" and lt < 0.5:
        k = 1-lt/0.5; yy, xx = np.ogrid[0:H, 0:W]; leak = np.exp(-(((xx-W*0.7)/(W*0.5))**2+((yy-H*0.4)/(H*0.6))**2))[..., None]
        out = out + k*leak*np.array([255, 150, 40])*1.4 + k*60
    elif kind == "glitch" and lt < 0.4:
        k = 1-lt/0.4; o = int(40*k); out[..., 0] = np.roll(out[..., 0], o, 1); out[..., 2] = np.roll(out[..., 2], -o, 1)
        rng = np.random.default_rng(int(lt*1000)+seed)
        for _ in range(8):
            y = int(rng.integers(0, H-60)); h = int(rng.integers(10, 60)); out[y:y+h] = np.roll(out[y:y+h], int(rng.integers(-120, 120)), 1)
    elif kind == "wipe" and lt < 0.45 and prev is not None:
        pr = eout(lt/0.45); x = int(W*pr); out[:, x:] = prev[:, x:].astype(np.float32)
        pw = np.asarray(paper(120, H, 9).convert("RGB")).astype(np.float32); x0 = max(0, min(W-120, x-60)); out[:, x0:x0+120] = pw[:, :min(120, W-x0)]
    return np.clip(out, 0, 255).astype(np.uint8)

# ---------- animierte Daten-Grafiken (engine/graphics.py) ----------
import graphics as _G
RENDER.update(_G.RENDER); DUR.update(_G.DUR); SOUNDS.update(_G.SOUNDS); SOUNDFN.update(_G.SOUNDFN); DATA = _G.DATA

# Endkarte: Frage tippt sich mit Tastatursound ein (Laurin 17.11.), dazu die festen Sounds aus SOUNDS["endcard"]
def _endcard_keys(p, dur):
    q = p.get("question", "TELL US IN THE COMMENTS"); ev = []; k = 0
    for ch in q:
        if ch != " " and k % 2 == 0: ev.append((0.6+k/22, f"key{k % 8}", 0.45))
        k += 1
    return ev
SOUNDFN["endcard"] = _endcard_keys

# Landkarte: Ortsnamen tippen sich mit Tastatursound ein (Laurin 17.11.), Schrift 18 Zeichen/s ab Pin + 0,3 s
def _route_keys(p, dur):
    ev = []
    for i, (lab, x, y) in enumerate(p["points"][:5]):
        t0 = 0.3+i*1.0+0.3
        for k, ch in enumerate(lab):
            if ch != " ": ev.append((t0+k/18, f"key{(i*3+k) % 8}", 0.45))
    return ev
SOUNDFN["route"] = _route_keys
