"""Kostenlose „Leben im Bild“-Effekte (Laurin 16.11.: Bilder sollen sich bewegen, nicht nur die Kamera).
Alles prozedural auf der CPU, keine Credits.

Quell-Ebene (bewegt sich mit der 2.5D-Kamera mit):  src(img, key, t, tags)
  - Licht lebt: helle Stellen (Lampen, Neon, Bildschirme) pulsieren/flackern + atmender Glow
  - "wet":  Spiegelungen am Boden schimmern (Wellen-Verzerrung nur auf hellen Reflexen in der unteren Bildhälfte)
  - "rays": Lichtstrahlen aus der hellsten Lampe (Volumen-Licht), atmen langsam
Bild-Ebene (über dem fertigen Frame):  screen(fr, key, t, tags, seed)
  - Nebel/Dunst zieht (immer leicht; "fog" = stärker)
  - "money": fallende Münzen + Geldscheine
  - "flash": Handy-/Kamera-Blitze in Menschenmengen
  - "cars":  Scheinwerfer-Lichtschwenk + Lens-Streak (Straßen)
  - "screens": zufälliges Bildschirm-Flimmern (Büros, Server)
"""
import math, numpy as np, cv2

_SRC = {}
def _prep(img, key):
    if key in _SRC: return _SRC[key]
    h, w = img.shape[:2]
    L = cv2.cvtColor(np.clip(img, 0, 255).astype(np.uint8), cv2.COLOR_RGB2GRAY).astype(np.float32)/255
    Lb = cv2.GaussianBlur(L, (0, 0), 3)
    bright = np.clip((Lb-0.55)/0.35, 0, 1)**1.5
    bright = cv2.GaussianBlur(bright, (0, 0), 4)
    glow = cv2.GaussianBlur(img*bright[..., None], (0, 0), w/60)
    # Reflexe unten (Boden): helle Stellen in unterer Hälfte
    yy = np.linspace(0, 1, h, dtype=np.float32)[:, None]
    wet = bright*np.clip((yy-0.55)/0.15, 0, 1)
    wet = cv2.GaussianBlur(wet, (0, 0), 6)
    # Lichtstrahlen: Zoom-Blur des Hellbereichs um die hellste Stelle der oberen 65 %
    up = cv2.GaussianBlur(L, (0, 0), w/80); up[int(h*0.65):] = 0
    cy, cx = np.unravel_index(np.argmax(up), up.shape)
    src = (bright[..., None]*img)
    acc = np.zeros_like(img)
    for i, s in enumerate(np.linspace(1.0, 1.9, 10)):
        M = np.float32([[s, 0, cx-cx*s], [0, s, cy-cy*s]])
        acc += cv2.warpAffine(src, M, (w, h), flags=cv2.INTER_LINEAR)*(1-i/12)
    rays = cv2.GaussianBlur(acc/6, (0, 0), 6)
    # zufällige Flacker-Phasen pro Lichtquelle (über Blob-Labels)
    nb, lab = cv2.connectedComponents((bright > 0.25).astype(np.uint8))
    rng = np.random.default_rng(abs(hash(key)) % 2**32)
    ph = rng.uniform(0, 6.28, nb+1).astype(np.float32); fq = rng.uniform(0.6, 2.2, nb+1).astype(np.float32)
    flick = rng.random(nb+1) < 0.25          # jede 4. Lichtquelle flackert unruhig (Neon)
    d = dict(bright=bright, glow=glow, wet=wet, rays=rays, lab=lab, ph=ph, fq=fq, flick=flick, c=(cx, cy))
    _SRC.clear(); _SRC[key] = d
    return d

def src(img, key, t, tags=()):
    d = _prep(img, key); h, w = img.shape[:2]
    # Licht pro Blob: Sinus-Atmen, manche flackern
    lab = d["lab"]; f = t*24
    amp = np.sin(t*d["fq"]*2*math.pi + d["ph"])*0.10
    r = np.random.default_rng(int(f)*7919).random(len(d["ph"]))
    amp = amp - np.where(d["flick"] & (r < 0.12), 0.35, 0.0)
    m = amp[lab]*d["bright"]
    out = img*(1+m[..., None])
    out += d["glow"]*(0.35+0.12*math.sin(t*1.3))
    if "wet" in tags:
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        dx = (np.sin(yy*0.09 + t*3.1)*3.5 + np.sin(yy*0.031 - t*1.7)*2.5)*d["wet"]
        dy = np.sin(xx*0.02 + t*2.3)*1.5*d["wet"]
        out = cv2.remap(out.astype(np.float32), xx+dx, yy+dy, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        out += d["wet"][..., None]*30*(0.5+0.5*np.sin(xx*0.05 + t*4))[..., None]
    if "rays" in tags:
        out += d["rays"]*(0.55+0.2*math.sin(t*0.9))
    return out

# ---------------- Bild-Ebene ----------------
_FOG = {}
def _fog(W, H, seed):
    if seed not in _FOG:
        rng = np.random.default_rng(seed)
        a = cv2.resize(rng.random((18, 32)).astype(np.float32), (W*2, H), interpolation=cv2.INTER_CUBIC)
        b = cv2.resize(rng.random((9, 16)).astype(np.float32), (W*2, H), interpolation=cv2.INTER_CUBIC)
        _FOG.clear(); _FOG[seed] = (cv2.GaussianBlur(a, (0, 0), 30), cv2.GaussianBlur(b, (0, 0), 60))
    return _FOG[seed]

class Particles:
    def __init__(self, kind, W, H, seed):
        r = np.random.default_rng(seed); self.k, self.W, self.H = kind, W, H
        n = 14
        self.x = r.uniform(0, W, n); self.y0 = r.uniform(-H, H, n); self.z = r.uniform(0.3, 1, n)
        self.rot = r.uniform(0, 6.28, n); self.sp = r.uniform(0.6, 1.4, n); self.bill = r.random(n) < 0.45
    def draw(self, fr, t):
        lay = np.zeros_like(fr); a = np.zeros(fr.shape[:2], np.float32)
        for x, y0, z, ro, sp, bill in zip(self.x, self.y0, self.z, self.rot, self.sp, self.bill):
            y = (y0 + t*(90+170*z)*sp) % (self.H+200) - 100
            xx = x + 40*math.sin(t*1.3*sp + ro)
            ang = ro + t*2.2*sp
            if bill:
                bw = 170*z+50; bh = bw*0.43; sx = abs(math.cos(ang))*bw+6
                box = cv2.boxPoints(((xx, y), (sx, bh), math.degrees(ro+t*0.7)))
                col = (150, 180, 140); cv2.fillPoly(lay, [box.astype(np.int32)], col, cv2.LINE_AA); cv2.fillPoly(a, [box.astype(np.int32)], 0.85, cv2.LINE_AA)
                cv2.polylines(lay, [box.astype(np.int32)], True, (80, 110, 75), 2, cv2.LINE_AA)
            else:
                rx = max(3, int(abs(math.cos(ang))*(26*z+10))); ry = int(26*z+10)
                c = (235, 190, 80) if math.cos(ang) > 0 else (200, 150, 50)
                cv2.ellipse(lay, (int(xx), int(y)), (rx, ry), 0, 0, 360, c, -1, cv2.LINE_AA); cv2.ellipse(a, (int(xx), int(y)), (rx, ry), 0, 0, 360, 1.0, -1, cv2.LINE_AA)
        a = cv2.GaussianBlur(a, (0, 0), 2.2)[..., None]*0.92
        return fr*(1-a) + cv2.GaussianBlur(lay, (0, 0), 2.0)*a

_P = {}
def screen(fr, key, t, tags=(), seed=1):
    H, W = fr.shape[:2]
    a, b = _fog(W, H, seed)
    k = 0.10 if "fog" not in tags else 0.22
    off1 = int(t*28) % W; off2 = int(t*12) % W
    fog = 0.6*a[:, off1:off1+W] + 0.4*b[:, off2:off2+W]
    tint = np.array([150, 160, 175], np.float32) if "cold" in tags else np.array([180, 160, 135], np.float32)
    fr = fr*(1-k*fog[..., None]) + tint*(k*fog[..., None])
    if "money" in tags or "glint" in tags:
        # Glanzlicht wandert diagonal über Geld/Metall (nur auf mittelhellen Flächen)
        per = 3.2; u = (t % per)/per
        if u < 0.55:
            v = u/0.55
            if ("g", W, H) not in _P: 
                yy, xx = np.mgrid[0:H, 0:W].astype(np.float32); _P[("g", W, H)] = (xx + yy*0.6)/(W + H*0.6)
            diag = _P[("g", W, H)]
            band = np.exp(-((diag - (-0.15 + 1.3*v))/0.05)**2)*math.sin(v*math.pi)
            lum = fr.mean(axis=2)/255
            wgt = np.clip((lum-0.18)*2.5, 0, 1)*band
            fr = fr + wgt[..., None]*np.array([255, 235, 190], np.float32)*0.55
    if "flash" in tags:
        r = np.random.default_rng(int(t*24)*31+seed)
        for _ in range(2):
            if r.random() < 0.10:
                x, y = int(r.uniform(0.05, 0.95)*W), int(r.uniform(0.25, 0.8)*H)
                g = np.zeros((H, W), np.float32); cv2.circle(g, (x, y), 6, 1.0, -1); g = cv2.GaussianBlur(g, (0, 0), 25)*6
                fr = fr + np.clip(g, 0, 1)[..., None]*255; fr = fr*1.03
    if "cars" in tags:
        per = 4.5; u = (t % per)/per
        if u < 0.45:
            v = u/0.45; xc = -0.2*W + 1.4*W*v
            xx = np.arange(W, dtype=np.float32)
            band = np.exp(-((xx-xc)/(W*0.12))**2)*math.sin(v*math.pi)
            fr = fr + band[None, :, None]*np.array([255, 225, 180], np.float32)*0.22
            yy = int(H*0.62); s = np.zeros((H, W), np.float32); cv2.line(s, (int(xc-W*0.3), yy), (int(xc+W*0.3), yy), 1.0, 3)
            fr = fr + cv2.GaussianBlur(s, (0, 0), 3)[..., None]*np.array([255, 210, 170], np.float32)*0.5*math.sin(v*math.pi)
    if "screens" in tags:
        r = np.random.default_rng(int(t*12)+seed)
        fr = fr*(1+0.015*(r.random()-0.5))
    return np.clip(fr, 0, 255)
