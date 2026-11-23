"""Texturen fuer die ANOM-Stilprobe (PIL). Alles fiktiv, keine echten Logos."""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import random, os
OUT = "/home/claude/anom/tex"; os.makedirs(OUT, exist_ok=True)
F = "/usr/share/fonts/opentype/inter/"
def font(w, s): return ImageFont.truetype(F + {"b": "Inter-Bold.otf", "m": "Inter-Medium.otf", "r": "Inter-Regular.otf", "x": "Inter-ExtraBold.otf"}[w], s)

AMBER = (255, 176, 46); RED = (235, 52, 52)

def phone_screen(state="chat"):
    W, H = 720, 1520
    im = Image.new("RGB", (W, H), (9, 11, 15)); d = ImageDraw.Draw(im)
    d.text((40, 30), "02:47", font=font("m", 30), fill=(200, 205, 215))
    d.text((W-160, 32), "LTE", font=font("m", 26), fill=(160, 165, 175))
    for i in range(4): d.rectangle([W-100+i*16, 62-i*8-8, W-90+i*16, 62], fill=(180, 185, 195))
    if state == "off":
        im = Image.new("RGB", (W, H), (6, 6, 8)); d = ImageDraw.Draw(im)
        d.text((W/2, H/2-40), "VERBINDUNG", font=font("x", 64), fill=RED, anchor="mm")
        d.text((W/2, H/2+40), "GETRENNT", font=font("x", 64), fill=RED, anchor="mm")
        d.text((W/2, H/2+130), "Server nicht erreichbar", font=font("r", 30), fill=(150, 150, 160), anchor="mm")
        im.save(f"{OUT}/screen_off.png"); return
    # Kopfzeile mit Schloss
    d.rounded_rectangle([0, 90, W, 210], 0, fill=(16, 19, 26))
    d.rounded_rectangle([40, 118, 104, 182], 16, fill=AMBER)
    d.rectangle([60, 148, 84, 170], fill=(20, 16, 8)); d.arc([62, 128, 82, 156], 180, 360, fill=(20, 16, 8), width=5)
    d.text((126, 122), "ANOM", font=font("x", 40), fill=(240, 240, 245))
    d.text((126, 168), "Ende-zu-Ende verschlüsselt", font=font("r", 22), fill=AMBER)
    msgs = [(0, "Lieferung steht?"), (1, "Freitag. Hafen. 23 Uhr."), (0, "Wie viele?"), (1, "Wie besprochen."),
            (0, "Und die Cops?"), (1, "Keine Sorge. Hier liest niemand mit.")]
    y = 260
    for side, t in msgs:
        tw = d.textlength(t, font=font("m", 32)); bw = tw + 56
        x0 = 40 if side == 0 else W - 40 - bw
        d.rounded_rectangle([x0, y, x0+bw, y+78], 30, fill=(32, 36, 46) if side == 0 else (120, 78, 14))
        d.text((x0+28, y+21), t, font=font("m", 32), fill=(235, 236, 240))
        y += 104
    d.text((W-110, y-14), "✓✓", font=font("b", 24), fill=AMBER)
    # Eingabe + Fernloeschung
    d.rounded_rectangle([30, H-160, W-170, H-70], 44, fill=(24, 27, 35))
    d.text((70, H-130), "Nachricht…", font=font("r", 30), fill=(110, 114, 124))
    d.rounded_rectangle([W-150, H-160, W-30, H-70], 44, fill=RED)
    d.text((W-90, H-115), "WIPE", font=font("x", 26), fill=(255, 255, 255), anchor="mm")
    im.save(f"{OUT}/screen_chat.png")

def rack_front(seed):
    """Server-Frontplatte: Einschuebe, Luftschlitze (LEDs sind eigene Objekte)."""
    r = random.Random(seed); W, H = 256, 1024
    im = Image.new("RGB", (W, H), (22, 24, 28)); d = ImageDraw.Draw(im)
    y = 12
    while y < H-30:
        h = r.choice([38, 38, 76])
        d.rectangle([10, y, W-10, y+h-4], fill=(34, 37, 42), outline=(52, 56, 62))
        for x in range(60, W-30, 9): d.line([x, y+8, x, y+h-12], fill=(18, 19, 22), width=3)
        d.rectangle([18, y+10, 44, y+h-14], fill=(46, 50, 56))
        y += h
    im.save(f"{OUT}/rack_{seed}.png")

def banknote():
    """Fiktiver Geldschein (keine echte Waehrung)."""
    W, H = 512, 240
    im = Image.new("RGB", (W, H), (196, 186, 150)); d = ImageDraw.Draw(im)
    for i in range(0, W, 6): d.line([i, 0, i-60, H], fill=(186, 176, 140), width=2)
    d.rectangle([8, 8, W-8, H-8], outline=(110, 120, 90), width=6)
    d.ellipse([W-190, 40, W-40, 200], fill=(170, 165, 128), outline=(110, 120, 90), width=4)
    d.text((30, 30), "100", font=font("x", 60), fill=(90, 100, 70))
    d.text((30, 150), "BANKNOTE", font=font("b", 34), fill=(110, 118, 88))
    im.save(f"{OUT}/note.png")

def tag(text, sub, path):
    W, H = 420, 220
    im = Image.new("RGB", (W, H), (236, 232, 220)); d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W, 56], fill=RED)
    d.text((W/2, 28), "BEWEISMITTEL", font=font("x", 30), fill=(255, 255, 255), anchor="mm")
    d.text((24, 80), text, font=font("b", 40), fill=(30, 30, 34))
    d.text((24, 140), sub, font=font("m", 26), fill=(90, 90, 96))
    for i in range(24, W-24, 7): d.line([i, 186, i, 206 if i % 3 else 200], fill=(30, 30, 30), width=2)
    im.save(path)

def tape_brick():
    W, H = 512, 256
    im = Image.new("RGB", (W, H), (150, 118, 72)); d = ImageDraw.Draw(im)
    r = random.Random(3)
    for i in range(60):
        x = r.randint(-50, W); d.line([x, 0, x + r.randint(-80, 80), H], fill=(170, 136, 86) if i % 2 else (132, 102, 60), width=r.randint(8, 30))
    im = im.filter(ImageFilter.GaussianBlur(1.2)); im.save(f"{OUT}/brick.png")

if __name__ == "__main__":
    phone_screen("chat"); phone_screen("off")
    for s in range(4): rack_front(s)
    banknote(); tape_brick()
    tag("FALL 21-0607", "Mobiltelefon · ANOM", f"{OUT}/tag1.png")
    tag("POS. 044", "Bargeld · gezählt", f"{OUT}/tag2.png")
    tag("POS. 112", "Substanz · 1 kg", f"{OUT}/tag3.png")
    print("ok")
