"""Thumbnail Video 004: Hero-Stil + Themenzeile 'GTA 5' (eigene Schrift, kein Logo, kein Glow, schwarzer Rand).
usage (im Repo-Root): python3 videos/004-gta5-money-machine/mk_thumb.py"""
import sys, json; sys.path.insert(0, 'engine'); import thumbnail as T
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np
V = "videos/004-gta5-money-machine"
def topic(out, txt="GTA 5"):
    img = Image.open(out).convert('RGBA'); W, H = img.size
    f = ImageFont.truetype(T.ANTON, 200)
    m = Image.new('L', (W, H), 0); ImageDraw.Draw(m).text((50, 18), txt, font=f, fill=255); bb = m.getbbox()
    g = np.zeros((H, W, 4), np.uint8); stops = [(0, (255, 236, 160)), (1, (222, 160, 40))]   # Gold-Verlauf (Kanalfarbe)
    for y in range(H):
        u = min(1, max(0, (y-bb[1])/max(1, bb[3]-bb[1]))); g[y, :, :3] = [int(stops[0][1][i]+(stops[1][1][i]-stops[0][1][i])*u) for i in range(3)]; g[y, :, 3] = 255
    sh = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ImageDraw.Draw(sh).text((62, 30), txt, font=f, fill=(0, 0, 0, 255), stroke_width=9, stroke_fill=(0, 0, 0, 255))
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(12)))
    ol = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ImageDraw.Draw(ol).text((50, 18), txt, font=f, fill=(0, 0, 0, 255), stroke_width=11, stroke_fill=(0, 0, 0, 255)); img.alpha_composite(ol)
    fill = Image.new('RGBA', (W, H), (0, 0, 0, 0)); fill.paste(Image.fromarray(g), (0, 0), m); img.alpha_composite(fill)
    img.convert('RGB').save(out, quality=92)
for t in ("a", "b", "c"):
    c = json.load(open(f"{V}/thumb_{t}.json")); out = f"{V}/thumb_{t}.jpg"; T.build(c, out); topic(out)
