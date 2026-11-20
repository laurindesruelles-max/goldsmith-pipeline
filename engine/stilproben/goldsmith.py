"""Stilprobe Goldsmith (20.11.2026): neue Effekte, ohne Ton.
Akte wird zugeschoben, Ort/Datum getippt, Wand waechst (Polaroids, Faeden, Stempel), Rueckzoom auf die ganze Wand, Lampe schwenkt.
Bilder aus dem Repo (fruehere Videos), 0 Credits."""
import math, subprocess, numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1920, 1080, 30
G = "/home/claude/repos/goldsmith-pipeline/"
import os; HOME = os.path.expanduser("~")
F_ANTON = f"{HOME}/.fonts/Anton.ttf"; F_TYPE = f"{HOME}/.fonts/SpecialElite.ttf"
IVORY = (242, 234, 216); RED = (200, 30, 40); INK = (30, 24, 20); GOLD = (222, 188, 104)
_F = {}
def font(p, s):
    k = (p, int(s))
    if k not in _F: _F[k] = ImageFont.truetype(p, int(s))
    return _F[k]
def ease(s): s = min(max(s, 0), 1); return s * s * (3 - 2 * s)
def eout(s): s = min(max(s, 0), 1); return 1 - (1 - s) ** 3
def load(p, w, h): return Image.open(p).convert("RGB").resize((w, h), Image.LANCZOS)

D = 19.0
# ---------- 1) Schreibtisch + Akte ----------
DESK = np.array(load(G + "assets/img/desk.png", 2400, 1350))
def folder_img():
    w, h = 900, 640
    im = Image.new("RGBA", (w + 80, h + 120), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0)); ImageDraw.Draw(sh).rectangle([50, 90, w + 50, h + 100], fill=(0, 0, 0, 190))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(18)))
    d.rounded_rectangle([30, 20, 330, 90], 14, fill=(196, 160, 104))
    d.rectangle([30, 60, w + 30, h + 60], fill=(208, 172, 112), outline=(150, 115, 70), width=4)
    d.text((80, 140), "CASE FILE  No. 03", font=font(F_TYPE, 56), fill=INK)
    d.text((80, 230), "THE LUXURY BONFIRE", font=font(F_ANTON, 92), fill=INK)
    d.line([(80, 360), (w - 40, 360)], fill=(120, 90, 50), width=3)
    d.text((80, 390), "Chapter 2  ·  Who gave the order?", font=font(F_TYPE, 44), fill=INK)
    st = Image.new("RGBA", (420, 150), (0, 0, 0, 0)); sd = ImageDraw.Draw(st)
    sd.rounded_rectangle([8, 8, 412, 142], 14, outline=RED, width=10); sd.text((210, 75), "CONFIDENTIAL", font=font(F_ANTON, 64), fill=RED, anchor="mm")
    im.alpha_composite(st.rotate(8, expand=True), (w - 430, h - 170))
    return im
FOLDER = folder_img()

def typed(layer, t, t0, text, xy, size=60, cps=14):
    if t < t0: return
    f = font(F_TYPE, size); d = ImageDraw.Draw(layer); n = int((t - t0) * cps); vis = text[:n]
    w = d.textlength(text, font=f)
    b = Image.new("RGBA", layer.size, (0, 0, 0, 0)); ImageDraw.Draw(b).rectangle([xy[0] - 30, xy[1] - 22, xy[0] + w + 60, xy[1] + size + 18], fill=(10, 10, 12, 185))
    layer.alpha_composite(b); d.text(xy, vis, font=f, fill=IVORY)
    if n <= len(text) and int(t * 2.5) % 2 == 0:
        cx = xy[0] + d.textlength(vis, font=f) + 6; d.rectangle([cx, xy[1] + 8, cx + size * 0.45, xy[1] + size], fill=GOLD)

def seg_desk(t):
    u = t / 4.4; z = 1.0 + 0.08 * u
    cw, ch = int(2400 / (1.25 * z)), int(1350 / (1.25 * z))
    x0 = int((2400 - cw) * (0.45 + 0.1 * u)); y0 = int((1350 - ch) * 0.5)
    fr = Image.fromarray(cv2.resize(DESK[y0:y0 + ch, x0:x0 + cw], (W, H))).convert("RGBA")
    if t > 0.5:  # Akte wird ins Bild geschoben
        p = eout((t - 0.5) / 0.9)
        rot = -14 * (1 - p) + 2 * p
        im = FOLDER.rotate(rot, expand=True, resample=Image.BICUBIC)
        x = int(W * 0.5 - im.width / 2 + 1100 * (1 - p)); y = int(H * 0.5 - im.height / 2 + 500 * (1 - p))
        fr.alpha_composite(im, (x, y))
    typed(fr, t, 2.0, "PARIS, 2017", (110, 90))
    return np.array(fr.convert("RGB"))

# ---------- 2) Die Wand waechst ----------
CW, CH = 2880, 1620
BOARD = load(G + "assets/img/board.png", CW, CH).convert("RGBA")
def polaroid(path, caption, w=430, rot=0, box=None):
    src = Image.open(path).convert("RGB")
    if box: src = src.crop(box)
    s = min(src.size); src = src.crop(((src.width - s) // 2, (src.height - s) // 2, (src.width + s) // 2, (src.height + s) // 2))
    ph = src.resize((w - 44, w - 44), Image.LANCZOS)
    fr = Image.new("RGBA", (w, w + 70), (238, 233, 222, 255)); fr.paste(ph, (22, 22))
    ImageDraw.Draw(fr).text((w / 2, w + 22), caption, font=font(F_TYPE, 40), fill=INK, anchor="mm")
    pad = 60; c = Image.new("RGBA", (w + 2 * pad, w + 70 + 2 * pad), (0, 0, 0, 0))
    sh = Image.new("RGBA", c.size, (0, 0, 0, 0)); ImageDraw.Draw(sh).rectangle([pad + 10, pad + 16, pad + w + 10, pad + w + 86], fill=(0, 0, 0, 170))
    c.alpha_composite(sh.filter(ImageFilter.GaussianBlur(14))); c.alpha_composite(fr, (pad, pad))
    return c.rotate(rot, expand=False, resample=Image.BICUBIC)
V = G + "videos/"
ITEMS = [  # (zeit, bild, x, y)  -- x,y = Mitte auf der Wand
    (4.9, polaroid(V + "002-luxury-bonfire/hero.png", "THE BONFIRE", rot=-4, box=(900, 0, 1344, 752)), 760, 560),
    (6.6, polaroid(V + "001-luxottica/g_sport.png", "THE BRAND", rot=5), 1500, 470),
    (8.3, polaroid(V + "003-gta6-money/hero_case.png", "THE STOCK", rot=-3, box=(700, 0, 1344, 752)), 2160, 640),
    (10.0, polaroid(V + "001-luxottica/hero_price.png", "THE PRICE", rot=4, box=(600, 0, 1344, 752)), 1420, 1120),
]
PINS = [(x, y - 260) for _, _, x, y in ITEMS]
THREADS = [(5.9 + 1.7 * k, k, k + 1) for k in range(3)] + [(11.2, 0, 3)]
STAMP_T = 12.0
def stamp_img(text, size=150, rot=-9):
    f = font(F_ANTON, size); tw = int(ImageDraw.Draw(Image.new("L", (1, 1))).textlength(text, font=f))
    st = Image.new("RGBA", (tw + 120, int(size * 1.75)), (0, 0, 0, 0)); sd = ImageDraw.Draw(st)
    sd.rounded_rectangle([14, 14, st.width - 14, st.height - 14], radius=18, outline=(205, 25, 35), width=12)
    sd.text((st.width / 2, st.height / 2), text, font=f, fill=(205, 25, 35), anchor="mm")
    a = np.array(st.getchannel("A")).astype(np.float32)
    noise = cv2.GaussianBlur(np.random.default_rng(4).random(a.shape).astype(np.float32), (0, 0), 2.2)
    a *= np.clip((noise - 0.36) * 6, 0.25, 1); st.putalpha(Image.fromarray(a.astype(np.uint8)))
    return st.rotate(rot, expand=True, resample=Image.BICUBIC)
STAMP = stamp_img("DESTROYED ON PURPOSE", size=105)

def wall_at(t):
    c = BOARD.copy()
    for t0, im, x, y in ITEMS:
        if t < t0: continue
        p = eout((t - t0) / 0.3); s = 1.25 - 0.25 * p
        im2 = im.resize((int(im.width * s), int(im.height * s)), Image.BILINEAR) if s != 1 else im
        c.alpha_composite(im2, (int(x - im2.width / 2), int(y - im2.height / 2)))
    arr = np.array(c)
    for t0, a, b in THREADS:
        if t < t0: continue
        p = eout((t - t0) / 0.7); (x0, y0), (x1, y1) = PINS[a], PINS[b]
        pts = []
        for i in range(31):
            u = i / 30 * p
            pts.append((x0 + (x1 - x0) * u, y0 + (y1 - y0) * u + 70 * math.sin(math.pi * u) * p))
        cv2.polylines(arr, [np.array(pts, np.int32)], False, (0, 0, 0, 255), 9, cv2.LINE_AA)
        cv2.polylines(arr, [np.array(pts, np.int32)], False, (190, 20, 30, 255), 6, cv2.LINE_AA)
    for k, (t0, *_r) in enumerate(ITEMS):
        if t >= t0 + 0.2:
            px, py = PINS[k]; cv2.circle(arr, (int(px), int(py)), 16, (170, 20, 25, 255), -1, cv2.LINE_AA); cv2.circle(arr, (int(px) - 5, int(py) - 5), 5, (255, 200, 200, 255), -1)
    c = Image.fromarray(arr)
    if t >= STAMP_T:
        p = eout((t - STAMP_T) / 0.11); s = 2.0 - p
        st = STAMP.resize((int(STAMP.width * s), int(STAMP.height * s)), Image.BILINEAR)
        c.alpha_composite(st, (int(2180 - st.width / 2), int(1190 - st.height / 2)))
    return np.array(c.convert("RGB"))

CAM = [(4.4, (1440, 810, 1.0)), (4.9, (760, 600, 2.0)), (6.4, (760, 600, 2.0)), (6.9, (1250, 560, 1.8)), (8.1, (1250, 560, 1.8)),
       (8.6, (1900, 620, 1.8)), (9.8, (1900, 620, 1.8)), (10.3, (1450, 1000, 1.8)), (11.6, (1450, 1000, 1.8)),
       (11.9, (1900, 1050, 1.6)), (13.2, (1900, 1050, 1.6)), (14.8, (1440, 810, 1.0)), (D, (1440, 810, 1.02))]
def cam(t):
    for (ta, a), (tb, b) in zip(CAM, CAM[1:]):
        if ta <= t <= tb:
            u = ease((t - ta) / (tb - ta)); z = math.exp(math.log(a[2]) + (math.log(b[2]) - math.log(a[2])) * u)
            return a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u, z
    return CAM[-1][1]

def seg_wall(t):
    img = wall_at(t); cx, cy, z = cam(t)
    s = z * W / CW
    sx = sy = 0
    if STAMP_T <= t < STAMP_T + 0.4: k = (1 - (t - STAMP_T) / 0.4) ** 2; sx, sy = 16 * k * math.sin(t * 93), 16 * k * math.cos(t * 71)
    M = np.float32([[s, 0, W / 2 - cx * s + sx], [0, s, H / 2 - cy * s + sy]])
    fr = cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
    if t > 15.2:  # Lampe schwenkt: Lichtkegel wandert, Rand wird dunkel
        u = ease((t - 15.2) / 3.2)
        lx = W * (0.25 + 0.55 * u); ly = H * 0.3
        yy, xx = np.ogrid[:H, :W]
        m = np.clip(1.3 - np.sqrt(((xx - lx) / 1.4) ** 2 + (yy - ly) ** 2) / 650, 0, 1)[..., None]
        k = min(1, (t - 15.2) / 0.6)
        fr = np.clip(fr * ((1 - k) + k * (0.15 + 1.1 * m)), 0, 255).astype(np.uint8)
    return fr

def frame(t):
    if t < 4.4: return seg_desk(t)
    fr = seg_wall(t)
    if t < 4.75:  # weicher Uebergang Schreibtisch -> Wand
        a = (t - 4.4) / 0.35; fr = (seg_desk(4.39) * (1 - a) + fr * a).astype(np.uint8)
    return fr

def grain(fr, i):
    n = np.random.default_rng(i).normal(0, 7, (H // 2, W // 2, 1)).astype(np.float32)
    return np.clip(fr + cv2.resize(n, (W, H))[..., None], 0, 255).astype(np.uint8)

out = "/home/claude/stilproben/stilprobe_goldsmith.mp4"
p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                      "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo", "-shortest", "-c:v", "libx264", "-preset", "veryfast", "-crf", "19",
                      "-pix_fmt", "yuv420p", "-c:a", "aac", out], stdin=subprocess.PIPE)
for i in range(int(D * FPS)):
    p.stdin.write(np.ascontiguousarray(grain(frame(i / FPS), i)).tobytes())
p.stdin.close(); p.wait(); print("ok")
