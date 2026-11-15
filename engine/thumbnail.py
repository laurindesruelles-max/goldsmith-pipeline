"""Goldsmith-Thumbnail (1280x720, Pinnwand-Stil).
Usage: python3 thumbnail.py config.json out.jpg
config: {"background": "img.png", "photos": [["img.png","CAPTION"], ...] (1-3),
         "lines": ["IT'S ALL", "ONE COMPANY"], "stamp": "CLASSIFIED"}
Schriften: ~/.fonts/Anton.ttf, SpecialElite.ttf (aus assets/fonts).
"""
import sys, json, os, random, numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

W, H = 1280, 720
HOME = os.path.expanduser("~")
ANTON = f"{HOME}/.fonts/Anton.ttf"; TYPE = f"{HOME}/.fonts/SpecialElite.ttf"
YELLOW = (255, 210, 63); RED = (215, 28, 38)

def cover(im, w, h):
    s = max(w/im.width, h/im.height); im = im.resize((int(im.width*s)+1, int(im.height*s)+1), Image.LANCZOS)
    x, y = (im.width-w)//2, (im.height-h)//2; return im.crop((x, y, x+w, y+h))

def polaroid(path, caption, w, rot):
    ph = cover(Image.open(path).convert("RGB"), w-30, w-30)
    ph = ImageEnhance.Contrast(ph).enhance(1.15)
    fr = Image.new("RGBA", (w, w+56), (240, 236, 226, 255)); fr.paste(ph, (15, 15))
    if caption: ImageDraw.Draw(fr).text((w/2, w+14), caption, font=ImageFont.truetype(TYPE, 34), fill=(30, 24, 20), anchor="mm")
    pad = 40; c = Image.new("RGBA", (w+2*pad, w+56+2*pad), (0, 0, 0, 0))
    sh = Image.new("RGBA", c.size, (0, 0, 0, 0)); ImageDraw.Draw(sh).rectangle([pad+8, pad+12, pad+w+8, pad+w+68], fill=(0, 0, 0, 200))
    c.alpha_composite(sh.filter(ImageFilter.GaussianBlur(12))); c.alpha_composite(fr, (pad, pad))
    return c.rotate(rot, expand=True, resample=Image.BICUBIC)

def stamp(text, size=64, rot=-12):
    f = ImageFont.truetype(ANTON, size); tw = int(ImageDraw.Draw(Image.new("L", (1, 1))).textlength(text, font=f))
    st = Image.new("RGBA", (tw+70, int(size*1.7)), (0, 0, 0, 0)); d = ImageDraw.Draw(st)
    d.rounded_rectangle([8, 8, st.width-8, st.height-8], radius=12, outline=RED, width=8)
    d.text((st.width/2, st.height/2), text, font=f, fill=RED, anchor="mm")
    a = np.array(st.getchannel("A")).astype(np.float32); n = cv2.GaussianBlur(np.random.default_rng(2).random(a.shape).astype(np.float32), (0, 0), 1.8)
    st.putalpha(Image.fromarray((a*np.clip((n-0.33)*6, 0.3, 1)).astype(np.uint8)))
    return st.rotate(rot, expand=True, resample=Image.BICUBIC)

def fit_font(text, maxw, start):
    s = start
    while s > 40:
        f = ImageFont.truetype(ANTON, s)
        if ImageDraw.Draw(Image.new("L", (1, 1))).textlength(text, font=f) <= maxw: return f
        s -= 4
    return ImageFont.truetype(ANTON, s)

def build_hero(cfg, out):
    """Variante mit einem starken Hero-Bild (Objekt/Gesicht rechts, Text links)."""
    img = cover(Image.open(cfg["background"]).convert("RGB"), W, H)
    img = ImageEnhance.Contrast(img).enhance(1.12); img = ImageEnhance.Color(img).enhance(1.1)
    a = np.asarray(img).astype(np.float32); xx = np.arange(W)[None, :, None]
    a *= np.clip(0.35 + 0.65*(xx/(W*0.55)), 0.35, 1.0)
    img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")
    if cfg.get("tag"):
        tg = dict(cfg["tag"])
        if tg.get("xy", "auto") == "auto":  # leeres Preisschild automatisch finden (größte helle Fläche)
            a = np.asarray(img.convert("RGB")).astype(int)
            m = ((a.min(2) > 190) & (np.abs(a[..., 0]-a[..., 2]) < 40)).astype(np.uint8)
            n, lab, st, cen = cv2.connectedComponentsWithStats(m)
            if n > 1:
                i = 1+int(np.argmax(st[1:, 4])); cnt, _ = cv2.findContours((lab == i).astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                (rx, ry), (rw, rh), ang = cv2.minAreaRect(cnt[0])
                if rw > rh: rw, rh, ang = rh, rw, ang+90
                tg["xy"] = [cen[i][0], cen[i][1]+0.08*rh]; tg.setdefault("rot", -ang); tg.setdefault("size", int(rw*0.55))
            else: tg["xy"] = [W*0.8, H*0.6]
        f = ImageFont.truetype(ANTON, tg.get("size", 80))
        t = Image.new("RGBA", (600, 300), (0, 0, 0, 0)); ImageDraw.Draw(t).text((300, 150), tg["text"], font=f, fill=RED, anchor="mm")
        t = t.rotate(tg.get("rot", 0), resample=Image.BICUBIC); img.alpha_composite(t, (int(tg["xy"][0]-300), int(tg["xy"][1]-150)))
    lines = cfg["lines"]; y = cfg.get("y", 150)
    for i, line in enumerate(lines):
        col = YELLOW if i == len(lines)-1 else (255, 255, 255)
        f = fit_font(line, cfg.get("maxw", 640), 200)
        sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(sh).text((62, y+10), line, font=f, fill=(0, 0, 0, 255))
        img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10)))
        ImageDraw.Draw(img).text((50, y), line, font=f, fill=col, stroke_width=7, stroke_fill=(0, 0, 0))
        y += int(f.size*1.08)
    if cfg.get("stamp"):
        st = stamp(cfg["stamp"]); img.alpha_composite(st, (60, min(y+10, H-st.height-30)))
    img.convert("RGB").save(out, quality=92)

def build(cfg, out):
    if cfg.get("mode") == "hero": return build_hero(cfg, out)
    bg = cover(Image.open(cfg["background"]).convert("RGB"), W, H)
    bg = ImageEnhance.Brightness(bg.filter(ImageFilter.GaussianBlur(3))).enhance(0.45)
    # warm spotlight right, dark left for text
    yy, xx = np.mgrid[0:H, 0:W]; light = np.exp(-(((xx-900)/520)**2 + ((yy-330)/380)**2))
    grad = np.clip(0.55 + 0.75*light - 0.35*np.clip((640-xx)/640, 0, 1), 0.15, 1.3)[..., None]
    arr = np.clip(np.asarray(bg).astype(np.float32)*grad*np.array([1.08, 0.98, 0.85]), 0, 255).astype(np.uint8)
    img = Image.fromarray(arr).convert("RGBA")
    photos = cfg["photos"][:3]
    spots = {1: [(960, 360, 390, -4)], 2: [(840, 330, 310, -7), (1100, 400, 310, 6)],
             3: [(810, 215, 250, -8), (1125, 235, 250, 7), (975, 520, 260, -2)]}[len(photos)]
    pins = []
    for (p, cap), (x, y, w, r) in zip(photos, spots):
        pl = polaroid(p, cap, w, r); img.alpha_composite(pl, (int(x-pl.width/2), int(y-pl.height/2))); pins.append((x, y-w/2-10))
    d = ImageDraw.Draw(img); cx, cy = (975, 345) if len(pins) == 3 else (970, 230)
    if len(pins) > 1:
        for px, py in pins:
            d.line([(px, py), (cx, cy)], fill=(120, 8, 14), width=8); d.line([(px, py), (cx, cy)], fill=(225, 30, 40), width=5)
            d.ellipse([px-11, py-11, px+11, py+11], fill=(225, 30, 40), outline=(70, 0, 0), width=3)
        d.ellipse([cx-16, cy-16, cx+16, cy+16], fill=(235, 35, 45), outline=(70, 0, 0), width=3)
    # headline
    lines = cfg["lines"]; y = 120 if len(lines) == 2 else 70
    for i, line in enumerate(lines):
        col = YELLOW if i == len(lines)-1 else (255, 255, 255)
        f = fit_font(line, 560, 190 if len(lines) == 2 else 150)
        sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(sh).text((62, y+10), line, font=f, fill=(0, 0, 0, 255))
        img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10)))
        ImageDraw.Draw(img).text((50, y), line, font=f, fill=col, stroke_width=6, stroke_fill=(0, 0, 0))
        y += int(f.size*1.08)
    if cfg.get("stamp"):
        st = stamp(cfg["stamp"]); img.alpha_composite(st, (60, min(y+10, H-st.height-30)))
    # vignette + subtle grain
    a = np.asarray(img.convert("RGB")).astype(np.float32)
    r = np.sqrt(((xx-W/2)/(W/2))**2+((yy-H/2)/(H/2))**2); a *= np.clip(1-0.35*np.clip(r-0.55, 0, 1), 0, 1)[..., None]
    a += np.random.default_rng(1).normal(0, 4, (H, W, 1))
    Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).save(out, quality=92)

if __name__ == "__main__":
    build(json.load(open(sys.argv[1])), sys.argv[2])
