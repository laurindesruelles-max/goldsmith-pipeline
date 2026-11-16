"""Nachbearbeitung der Diorama-Renders (960x540 -> 1920x1080):
Tilt-Shift (Modelleisenbahn-Unschärfe), Lichtstrahl (Volumenlicht), Staub im Gegenlicht, Kino-Grade (Teal/Orange).
Benutzung:  fr = post.frame(clip_dir, idx, params)   (idx = 1-basierter Frame des Renders)
params: focus (0..1, Höhe der Schärfeebene im Bild, Standard 0.55), band (0.16), blur (Max.-Unschärfe px, 10),
        beam (0..1.5, Stärke Lichtstrahl, 1.0), dust (0..2, Staubmenge/-helligkeit, 1.0; 0 = aus), grade (0..1, 1.0),
        warm (Farbstimmung -1 kühl .. +1 warm, 0.3)
"""
import os, json, math, numpy as np, cv2

W, H = 1920, 1080
_META = {}; _MASK = {}


def meta(clip):
    if clip not in _META:
        p = f"{clip}/meta.json"; _META[clip] = json.load(open(p)) if os.path.exists(p) else {"frames": {}}
    return _META[clip]


def nframes(clip):
    return len([f for f in os.listdir(clip) if f.startswith("f_") and f.endswith(".png")])


def tilt_weights(focus, band):
    k = (round(focus, 3), round(band, 3))
    if k not in _MASK:
        y = np.linspace(0, 1, H, dtype=np.float32); d = np.clip((np.abs(y-focus)-band)/(0.5-band+1e-6), 0, 1)
        _MASK[k] = (d**1.2)[:, None, None]
    return _MASK[k]


def tiltshift(img, focus=0.55, band=0.16, blur=10):
    if blur <= 0: return img
    w = tilt_weights(focus, band)
    b1 = cv2.GaussianBlur(img, (0, 0), blur*0.45); b2 = cv2.GaussianBlur(img, (0, 0), blur)
    w1 = np.clip(w*2, 0, 1); w2 = np.clip(w*2-1, 0, 1)
    out = img*(1-w1) + b1*w1
    return out*(1-w2) + b2*w2


def _px(p):
    return (p[0]*W, (1-p[1])*H)


def beam_mask(fm):
    """Maske (H,W) des Lichtstrahls aus projizierten Ecken (konvexe Hülle), weich, mit Verlauf zum Fenster hin."""
    out = []
    for b in fm.get("beams", []):
        near = [_px(p) for p in b["near"] if p[2] > 0]; far = [_px(p) for p in b["far"] if p[2] > 0]
        if len(near) + len(far) < 3: out.append(None); continue
        small = np.zeros((H//4, W//4), np.float32)
        hull = cv2.convexHull(np.array([(x/4, y/4) for x, y in near+far], np.float32)).astype(np.int32)
        cv2.fillConvexPoly(small, hull, 1.0)
        # Verlauf: am Fenster hell, zum Boden schwächer
        nc = np.mean(np.array(near), 0)/4; fc = np.mean(np.array(far), 0)/4
        yy, xx = np.mgrid[0:H//4, 0:W//4].astype(np.float32); v = fc-nc; L2 = float(v @ v) + 1e-6
        u = np.clip(((xx-nc[0])*v[0]+(yy-nc[1])*v[1])/L2, 0, 1)
        small *= (1-0.75*u)
        small = cv2.GaussianBlur(small, (0, 0), 9)
        out.append((cv2.resize(small, (W, H), interpolation=cv2.INTER_LINEAR), b))
    return out


def dust_layer(fm, beams, gain=1.0, focus=0.55, band=0.16, seed=0):
    """Staubkörnchen: im Lichtstrahl hell (Gegenlicht), außerhalb kaum sichtbar."""
    lay = np.zeros((H, W), np.float32)
    bm = [b[0] if b else None for b in beams]
    for pts in fm.get("dust", []):
        for x, y, z, sz, bi in pts:
            px, py = int(x*W), int((1-y)*H)
            if not (0 <= px < W and 0 <= py < H): continue
            inb = bm[bi][py, px] if bi < len(bm) and bm[bi] is not None else 0.0
            lum = 0.02 + 0.9*inb**1.5
            if lum < 0.06: continue
            r = max(1.0, (1.2 + 2.3*sz) * 4.0/max(z, 0.6))
            dfoc = max(0, abs(py/H-focus)-band)
            r += dfoc*14                           # außerhalb der Schärfe: größer, weicher (Bokeh)
            a = lum*(0.35+0.65*sz)/(1+dfoc*6)*0.75
            cv2.circle(lay, (px, py), int(round(r)), float(a), -1, lineType=cv2.LINE_AA)
    lay = cv2.GaussianBlur(lay, (0, 0), 1.4) + 0.5*cv2.GaussianBlur(lay, (0, 0), 6)
    return lay*gain


def grade(img, amount=1.0, warm=0.3):
    """Teal-Schatten / Orange-Lichter, mehr Kontrast und Sättigung (VANTAGE-Look)."""
    x = img/255.0
    lum = (0.299*x[..., 0]+0.587*x[..., 1]+0.114*x[..., 2])[..., None]
    sh = np.clip(1-lum*2.2, 0, 1); hi = np.clip(lum*1.6-0.5, 0, 1)
    teal = np.array([-0.035, 0.012, 0.05]); orange = np.array([0.06, 0.02, -0.05])
    x = x + amount*(sh*teal*(1-0.5*warm) + hi*orange*(0.6+warm))
    m = lum; x = m + (x-m)*(1+0.18*amount)                       # Sättigung
    x = np.clip(x, 0, 1); x = x*x*(3-2*x)*0.35*amount + x*(1-0.35*amount)   # S-Kurve
    return np.clip(x*255, 0, 255)


def frame(clip, idx, p=None):
    p = p or {}
    n = nframes(clip); idx = max(1, min(n, idx))
    im = cv2.imread(f"{clip}/f_{idx:04d}.png", cv2.IMREAD_COLOR)[..., ::-1].astype(np.float32)
    im = cv2.resize(im, (W, H), interpolation=cv2.INTER_CUBIC)
    im = np.clip(im + 0.35*(im - cv2.GaussianBlur(im, (0, 0), 2)), 0, 255)       # leicht nachschärfen
    fm = meta(clip)["frames"].get(str(idx), {})
    focus, band, blur = p.get("focus", 0.55), p.get("band", 0.16), p.get("blur", 10)
    beams = beam_mask(fm) if p.get("beam", 1.0) > 0 else []
    for bb in beams:
        if bb is None: continue
        m, b = bb; col = np.array(b["color"], np.float32)*255
        im = im + m[..., None]*col*b["strength"]*0.6*p.get("beam", 1.0)
        im = im*(1-0.12*m[..., None]) + np.minimum(im*1.25, 255)*0.12*m[..., None]
    if p.get("dust", 1.0) > 0 and fm.get("dust"):
        d = dust_layer(fm, beams, p.get("dust", 1.0), focus, band, seed=idx)
        im = im + d[..., None]*np.array([255, 228, 185], np.float32)
    im = tiltshift(np.clip(im, 0, 255), focus, band, blur)
    im = grade(im, p.get("grade", 1.0), p.get("warm", 0.3))
    return im.astype(np.uint8)


if __name__ == "__main__":
    import sys
    clip, idx = sys.argv[1], int(sys.argv[2]); out = sys.argv[3]
    cv2.imwrite(out, frame(clip, idx, json.loads(sys.argv[4]) if len(sys.argv) > 4 else None)[..., ::-1])
