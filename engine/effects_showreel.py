"""Effekt-Showreel: 8 neue Effekte à ~4,5 s, beschriftet. Schreibt reel_video.mp4 + reel_sfx.json"""
import os, sys, math, json, random, subprocess, numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter
W, H, FPS = 1920, 1080, 30
F = os.path.expanduser("~/.fonts")
ANTON = f"{F}/Anton.ttf"; TYPE = f"{F}/SpecialElite.ttf"; SERIF = f"{F}/playfair-display-latin-700-normal.ttf"; SERIF4 = f"{F}/playfair-display-latin-400-normal.ttf"
INTER = "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf"
GOLD = (222, 188, 104); IVORY = (242, 234, 216); RED = (205, 25, 35); INK = (28, 22, 18)
V = "/home/claude/goldsmith/video01"; A = f"{V}/v3/a"
SFX = []
def f(p, s): return ImageFont.truetype(p, int(s))
def ease(s): s = min(max(s, 0), 1); return s*s*(3-2*s)
def eout(s): s = min(max(s, 0), 1); return 1-(1-s)**3
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
def over(fr, layer):
    a = np.asarray(layer)[..., 3:4].astype(np.float32)/255
    return (fr*(1-a)+np.asarray(layer)[..., :3]*a).astype(np.uint8)
def label(layer, n, txt):
    d = ImageDraw.Draw(layer); s = f"{n}  ·  {txt}"; tw = d.textlength(s, font=f(INTER, 34))
    layer.alpha_composite(Image.new("RGBA", (int(tw)+60, 70), (8, 9, 12, 215)), (60, 60)); d.rectangle([60, 60, 68, 130], fill=RED)
    d.text((92, 76), s, font=f(INTER, 34), fill=IVORY)
def typed_lines(d, t, t0, lines, xy, size, color=INK, cps=20, gap=1.25):
    k = int(max(0, t-t0)*cps); x, y = xy
    for ln in lines:
        d.text((x, y), ln[:max(0, k)], font=f(TYPE, size), fill=color); k -= len(ln)+3; y += size*gap

# ---------- shared props ----------
def paper(w, h, seed=1, tint=(234, 225, 200)):
    rng = np.random.default_rng(seed); a = np.full((h, w, 3), tint, np.float32)
    a += rng.normal(0, 6, (h, w, 1)); a *= (1-0.12*cv2.GaussianBlur(rng.random((h, w)).astype(np.float32), (0, 0), 40)[..., None]*2)
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")
DESK = load(f"{A}/desk.png", int(W*1.2), int(H*1.2))
def document():
    p = paper(1100, 1400, 3); d = ImageDraw.Draw(p)
    d.text((80, 70), "CONFIDENTIAL  —  INTERNAL MEMO", font=f(TYPE, 40), fill=(150, 30, 30))
    d.line([(80, 130), (1020, 130)], fill=INK, width=3)
    body = ["Re: Acquisition of the Ray-Ban brand", "", "Following the agreement signed this", "month, the company acquired Ray-Ban", "from Bausch & Lomb for $640 million.", "", "Distribution through discount outlets", "will be discontinued. Quality and", "pricing will be repositioned at the", "premium end of the market."]
    for i, ln in enumerate(body): d.text((80, 190+i*72), ln, font=f(TYPE, 46), fill=INK)
    return p
DOC = document()

# ---------- effects ----------
def e1_parallax(t, T):  # reuse rendered parallax probe
    global PCLIP
    k = min(int(t*FPS)+15, len(PCLIP)-1); return PCLIP[k], Image.new("RGBA", (W, H), (0, 0, 0, 0))

def e2_highlight(t, T):
    base = Image.fromarray(DESK).convert("RGBA"); doc = DOC.rotate(-3, expand=True, resample=Image.BICUBIC)
    sh = Image.new("RGBA", base.size, (0, 0, 0, 0)); ImageDraw.Draw(sh).rectangle([620, 120, 620+doc.width-40, 120+doc.height-40], fill=(0, 0, 0, 160))
    base.alpha_composite(sh.filter(ImageFilter.GaussianBlur(25))); base.alpha_composite(doc, (580, 70))
    # highlighter strokes on the "$640 million" line (line index 4)
    hl = Image.new("RGBA", base.size, (0, 0, 0, 0)); dh = ImageDraw.Draw(hl)
    for li, (t0, x0, x1) in enumerate([(1.6, 660, 1580), (2.2, 660, 1520)]):
        p = eout((t-t0)/0.45)
        if p > 0:
            y = 70+190+(li+3)*72+8+li*2; dh.rectangle([x0, y, x0+(x1-x0)*p, y+52], fill=(255, 230, 40, 120))
    base.alpha_composite(hl.rotate(0))
    arr = np.asarray(base.convert("RGB"))
    z = 1.0+1.1*ease(t/1.5); cy = 0.45+0.08*ease(t/1.5)
    return view(arr, 0.56, cy, z, rot=-1.5*ease(t/1.5)), Image.new("RGBA", (W, H), (0, 0, 0, 0))

def e3_redact(t, T):
    p = paper(W, H, 5).convert("RGB"); fr = np.asarray(p).copy()
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
    d.text((W/2, 260), "FILE NO. 001  —  OWNER OF RECORD", font=f(TYPE, 52), fill=INK, anchor="mm")
    d.text((W/2, 520), "LUXOTTICA", font=f(ANTON, 230), fill=(150, 20, 28), anchor="mm")
    d.text((W/2, 760), "ITALY  ·  FOUNDED 1961", font=f(TYPE, 52), fill=INK, anchor="mm")
    # bars slide away one by one
    for i, (y0, y1, t0) in enumerate([(220, 300, 1.0), (390, 650, 1.6), (720, 800, 2.4)]):
        p2 = eout((t-t0)/0.35); x = -W*p2*(1 if i % 2 == 0 else -1)
        if p2 < 1: d.rectangle([260+x, y0, W-260+x, y1], fill=(10, 10, 10, 255))
    zoom = 1.0+0.06*ease(t/T)
    return view(fr, 0.5, 0.5, zoom), layer

def e4_chart(t, T):
    g = paper(W, H, 7, (238, 236, 228)).convert("RGB"); fr = np.asarray(g).copy()
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
    for x in range(200, 1760, 80): d.line([(x, 220), (x, 900)], fill=(170, 190, 210, 120), width=1)
    for y in range(220, 901, 68): d.line([(200, y), (1720, y)], fill=(170, 190, 210, 120), width=1)
    d.text((200, 140), "OAKLEY SHARE PRICE  ·  1996", font=f(TYPE, 46), fill=INK)
    rng = random.Random(4); pts = []; v = 0.75
    for i in range(60):
        v += rng.uniform(-0.02, 0.025) if i < 30 else rng.uniform(-0.045, 0.012); pts.append((200+i*25.5, 220+(1-v)*680))
    n = int(len(pts)*eout(t/2.6))
    if n > 1:
        d.line(pts[:n], fill=(200, 20, 30, 255), width=8, joint="curve"); x, y = pts[n-1]; d.ellipse([x-12, y-12, x+12, y+12], fill=(200, 20, 30, 255))
    if t > 2.7:
        a = int(255*ease((t-2.7)/0.25)); s = 1+0.2*(1-eout((t-2.7)/0.3))
        d.text((1450, 560), "-33%", font=f(ANTON, 200*s), fill=(200, 20, 30, a), anchor="mm", stroke_width=6, stroke_fill=(255, 255, 255, a))
    return fr, layer

MAP = load(f"{A}/map.png", int(W*1.3), int(H*1.3))
def e5_route(t, T):
    z = 1.15+0.15*ease(t/T); fr = view(MAP, 0.5, 0.5, z)
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
    P = [((520, 640), "FACTORY", 0.3), ((1000, 420), "WAREHOUSE", 1.3), ((1450, 640), "STORE", 2.3)]
    for i, ((x, y), lab, t0) in enumerate(P):
        if i > 0:
            (px, py) = P[i-1][0]; p = eout((t-(t0-0.9))/0.8)
            if p > 0:
                segs = 28
                for s in range(int(segs*p)):
                    if s % 2 == 0:
                        a0, a1 = s/segs, (s+1)/segs
                        def bz(u): mx, my = (px+x)/2, min(py, y)-160; return ((1-u)**2*px+2*(1-u)*u*mx+u*u*x, (1-u)**2*py+2*(1-u)*u*my+u*u*y)
                        d.line([bz(a0), bz(a1)], fill=(205, 22, 32, 255), width=9)
        if t >= t0:
            p = eout((t-t0)/0.25); yy = y-200*(1-p)
            d.ellipse([x-26, yy-26, x+26, yy+26], fill=(210, 25, 35, 255), outline=(90, 0, 0, 255), width=4)
            if t > t0+0.3:
                vis = lab[:int((t-t0-0.3)*18)]; tw = d.textlength(lab, font=f(TYPE, 44))
                d.rectangle([x-tw/2-20, y+40, x+tw/2+20, y+105], fill=(240, 232, 210, 235)); d.text((x, y+72), vis, font=f(TYPE, 44), fill=INK, anchor="mm")
    return fr, layer

IMG18 = load(f"{V}/img/18.png", 960, 1080); IMG19 = load(f"{V}/img/19.png", 960, 1080)
def e6_split(t, T):
    p = eout((t-0.2)/0.6); fr = np.zeros((H, W, 3), np.uint8)
    lw = int(960*p) if p > 0 else 0
    fr[:, :W//2] = (IMG18*0.8).astype(np.uint8); fr[:, W//2:] = IMG19
    if p < 1: fr[:, W//2+int(960*p):] = 0; fr[:, W//2:W//2+int(960*p)] = IMG19[:, :int(960*p)]
    g = cv2.cvtColor(fr[:, :W//2], cv2.COLOR_RGB2GRAY); fr[:, :W//2] = cv2.cvtColor(g, cv2.COLOR_GRAY2RGB)
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
    d.rectangle([W//2-4, 0, W//2+4, H], fill=(240, 240, 240, 255))
    for x, txt, col, t0 in [(W//4, "BEFORE", (255, 255, 255), 0.5), (3*W//4, "AFTER", GOLD, 1.1)]:
        if t > t0:
            a = int(255*ease((t-t0)/0.25)); d.text((x, 900), txt, font=f(ANTON, 130), fill=col+(a,), anchor="mm", stroke_width=6, stroke_fill=(0, 0, 0, a))
    for x, txt, t0 in [(W//4, "BARGAIN BIN", 1.8), (3*W//4, "LUXURY ICON", 2.4)]:
        if t > t0: d.text((x, 1000), txt[:int((t-t0)*18)], font=f(TYPE, 46), fill=IVORY, anchor="mm")
    return fr, layer

IMGA = load(f"{V}/img/24.png", int(W*1.1), int(H*1.1)); IMGB = load(f"{V}/img/26.png", int(W*1.1), int(H*1.1)); IMGC = load(f"{V}/img/30.png", int(W*1.1), int(H*1.1)); IMGD = load(f"{V}/img/44.png", int(W*1.1), int(H*1.1))
def e7_transitions(t, T):
    seq = [IMGA, IMGB, IMGC, IMGD]; cut = [0, 1.25, 2.5, 3.75]; i = max(k for k, c in enumerate(cut) if t >= c); lt = t-cut[i]
    fr = view(seq[i], 0.5, 0.5, 1.0+0.05*lt).astype(np.float32)
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
    names = ["", "FILM BURN", "GLITCH", "PAPER WIPE"]
    if i == 1 and lt < 0.5:  # film burn: orange light leak
        k = 1-lt/0.5; yy, xx = np.mgrid[0:H, 0:W]; leak = np.exp(-(((xx-W*0.7)/(W*0.5))**2+((yy-H*0.4)/(H*0.6))**2))[..., None]
        fr = fr + k*leak*np.array([255, 150, 40])*1.4 + k*60
    if i == 2 and lt < 0.4:  # glitch: rgb split + slices
        k = 1-lt/0.4; o = int(40*k); fr[..., 0] = np.roll(fr[..., 0], o, 1); fr[..., 2] = np.roll(fr[..., 2], -o, 1)
        rng = np.random.default_rng(int(t*100))
        for _ in range(8):
            y = rng.integers(0, H-60); h = rng.integers(10, 60); fr[y:y+h] = np.roll(fr[y:y+h], rng.integers(-120, 120), 1)
    if i == 3 and lt < 0.45:  # paper wipe from right covering old image
        p = eout(lt/0.45); prev = view(seq[2], 0.5, 0.5, 1.0+0.05*1.25).astype(np.float32); x = int(W*p)
        fr[:, x:] = prev[:, x:]
        pw = np.asarray(paper(120, H, 9).convert("RGB")).astype(np.float32); x0 = max(0, min(W-120, x-60)); fr[:, x0:x0+120] = pw[:, :min(120, W-x0)]
    if i > 0 and lt < 1.0:
        d.text((W-80, H-80), names[i], font=f(INTER, 40), fill=IVORY+(int(255*min(1, (1-lt)*3)),), anchor="rs")
    return np.clip(fr, 0, 255).astype(np.uint8), layer

def clipping():
    w, h = 1100, 680; c = paper(w, h, 11); d = ImageDraw.Draw(c)
    d.text((50, 35), "THE FINANCIAL RECORD  ·  JUNE 2007", font=f(INTER, 30), fill=(60, 50, 40)); d.line([(50, 85), (w-50, 85)], fill=INK, width=4)
    d.text((50, 110), "EYEWEAR GIANT", font=f(SERIF, 100), fill=INK); d.text((50, 225), "SWALLOWS RIVAL", font=f(SERIF, 100), fill=INK)
    d.text((50, 360), "A $2.1 billion deal ends a decade-long feud", font=f(SERIF4, 42), fill=(55, 45, 38))
    for col in range(3):
        for r in range(9): d.line([(50+col*340, 440+r*24), (50+col*340+300, 440+r*24)], fill=(120, 110, 95), width=8)
    return c
CLIP = clipping(); NEWSBG = load(f"{V}/img/56.png", int(W*1.1), int(H*1.1))
def e8_spin(t, T):
    fr = (view(NEWSBG, 0.5, 0.5, 1.05)*0.45).astype(np.uint8); layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    p = eout(t/1.3); s = 0.05+0.95*p; rot = (1-p)*720+3
    im = CLIP.resize((max(2, int(CLIP.width*s)), max(2, int(CLIP.height*s)))).rotate(rot, expand=True, resample=Image.BICUBIC)
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); sh.alpha_composite(Image.new("RGBA", im.size, (0, 0, 0, 170)), (int(W/2-im.width/2+20), int(H/2-im.height/2+25)))
    layer.alpha_composite(sh.filter(ImageFilter.GaussianBlur(18))); layer.alpha_composite(im, (int(W/2-im.width/2), int(H/2-im.height/2)))
    if t > 2.0:  # stamp
        q = eout((t-2.0)/0.12); st = Image.new("RGBA", (760, 260), (0, 0, 0, 0)); sd = ImageDraw.Draw(st)
        sd.rounded_rectangle([10, 10, 750, 250], radius=16, outline=RED, width=14); sd.text((380, 130), "BREAKING", font=f(ANTON, 160), fill=RED, anchor="mm")
        st = st.rotate(-10, expand=True); sc = 2-q; st = st.resize((int(st.width*sc*0.8), int(st.height*sc*0.8)))
        st.putalpha(st.getchannel("A").point(lambda v: int(v*min(1, q*1.4)*0.92))); layer.alpha_composite(st, (int(W*0.68-st.width/2), int(H*0.72-st.height/2)))
    return fr, layer

EFFECTS = [("PARALLAX-3D", e1_parallax, 4.5, [(0.1, "whoosh", 0.4)]),
           ("DOKUMENT-ZOOM + TEXTMARKER", e2_highlight, 4.5, [(0.05, "paper", 0.5), (1.6, "NEW_highlighter", 0.9), (2.2, "NEW_highlighter", 0.8)]),
           ("SCHWÄRZUNG WIRD AUFGEDECKT", e3_redact, 4.5, [(1.0, "zip", 0.6), (1.6, "NEW_paper_tear", 0.9), (1.62, "NEW_sub_drop", 0.8), (2.4, "zip", 0.6)]),
           ("ANIMIERTES DIAGRAMM", e4_chart, 4.5, [(0.1, "NEW_heartbeat", 0.8)] + [(0.2+i*0.25, "tick", 0.3) for i in range(10)] + [(2.7, "NEW_sub_drop", 1.0)]),
           ("LANDKARTE MIT ROUTEN", e5_route, 4.5, [(0.3, "pin", 0.8), (1.3, "pin", 0.8), (2.3, "pin", 0.8), (0.5, "zip", 0.4), (1.5, "zip", 0.4)]),
           ("VORHER / NACHHER", e6_split, 4.5, [(0.2, "whoosh", 0.5), (0.5, "slap", 0.6), (1.1, "NEW_coins", 0.9)]),
           ("ÜBERGÄNGE", e7_transitions, 5.0, [(1.25, "NEW_film_projector", 0.8), (2.5, "NEW_glitch", 0.9), (3.75, "NEW_paper_tear", 0.7)]),
           ("ZEITUNGS-WIRBEL", e8_spin, 4.5, [(0.0, "whoosh", 0.6), (0.05, "riser", 0.4), (1.25, "NEW_flash", 0.9), (2.05, "stamp", 1.0)])]

if __name__ == "__main__":
    cap = cv2.VideoCapture("/home/claude/demoA/Probe_A_Parallax_3D.mp4"); PCLIP = []
    while True:
        ok, fr = cap.read()
        if not ok: break
        PCLIP.append(cv2.cvtColor(fr, cv2.COLOR_BGR2RGB))
    if sys.argv[1:] and sys.argv[1] == "still":
        for i, (nm, fn, T, _) in enumerate(EFFECTS):
            t = float(sys.argv[2]) if len(sys.argv) > 2 else T*0.7
            fr, layer = fn(min(t, T-0.01), T); label(layer, i+1, nm); Image.fromarray(over(fr, layer)).save(f"st_{i+1}.jpg", quality=85)
        sys.exit()
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", "reel_video.mp4"], stdin=subprocess.PIPE)
    t0 = 0.0; sfx = []
    for i, (nm, fn, T, ev) in enumerate(EFFECTS):
        for k in range(int(T*FPS)):
            t = k/FPS; fr, layer = fn(t, T); label(layer, i+1, nm); out = over(fr, layer)
            if t < 0.15: out = (out*(t/0.15)).astype(np.uint8)
            if t > T-0.15: out = (out*max(0, (T-t)/0.15)).astype(np.uint8)
            p.stdin.write(out.tobytes())
        sfx += [(t0+a, nm2, g) for a, nm2, g in ev]; t0 += int(T*FPS)/FPS
    p.stdin.close(); p.wait(); json.dump({"sfx": sfx, "total": t0}, open("reel_sfx.json", "w")); print("total", t0)
