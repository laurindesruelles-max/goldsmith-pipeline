"""2.5D-Kamerafahrt aus einem Standbild (kostenlos, CPU).
Depth Anything V2 Small (ONNX) schätzt Tiefe; pro Frame wird das Bild tiefenabhängig verschoben/gezoomt
→ Vordergrund bewegt sich stärker als Hintergrund (Parallaxe, „Vantage-Look“).

python3 depth25d.py depth <bild.png> <out_depth.png>
python3 depth25d.py test <bild.png> <out.mp4> [move] [sek]
"""
import sys, os, numpy as np, cv2
MODEL = os.environ.get("DEPTH_MODEL", "/home/claude/models/da2s.onnx")
_S = None

def depth(img_rgb):
    """img_rgb uint8 HxWx3 → Tiefe float32 HxW in [0,1], 1 = nah"""
    global _S
    import onnxruntime as ort
    if _S is None: _S = ort.InferenceSession(MODEL, providers=["CPUExecutionProvider"])
    h, w = img_rgb.shape[:2]; s = 518
    x = cv2.resize(img_rgb, (s*w//h//14*14, s), interpolation=cv2.INTER_AREA).astype(np.float32)/255
    x = (x-[0.485, 0.456, 0.406])/[0.229, 0.224, 0.225]
    d = _S.run(None, {"pixel_values": x.transpose(2, 0, 1)[None].astype(np.float32)})[0][0]
    d = cv2.resize(d, (w, h), interpolation=cv2.INTER_CUBIC)
    lo, hi = np.percentile(d, 2), np.percentile(d, 98)
    d = np.clip((d-lo)/(hi-lo+1e-6), 0, 1)
    d = cv2.GaussianBlur(d, (0, 0), max(3, w/300))          # weich, damit Kanten nicht reißen
    return d.astype(np.float32)

def load_depth(png, img_rgb):
    if os.path.exists(png): return cv2.imread(png, cv2.IMREAD_UNCHANGED).astype(np.float32)/65535
    d = depth(img_rgb); cv2.imwrite(png, (d*65535).astype(np.uint16)); return d

MOVES = {   # (dx, dy, zoom) als Anteil der Bildbreite über die ganze Fahrt; Parallaxe-Stärke par
    "push":   dict(dx=0.0,   dy=0.0,   z0=1.06, z1=1.16, par=0.045),
    "pull":   dict(dx=0.0,   dy=0.0,   z0=1.16, z1=1.06, par=0.045),
    "left":   dict(dx=-0.05, dy=0.0,   z0=1.12, z1=1.12, par=0.06),
    "right":  dict(dx=0.05,  dy=0.0,   z0=1.12, z1=1.12, par=0.06),
    "rise":   dict(dx=0.0,   dy=-0.04, z0=1.12, z1=1.14, par=0.05),
    "orbit":  dict(dx=0.045, dy=-0.015, z0=1.10, z1=1.15, par=0.07),
}

def frame(img, d, u, move="push", W=1920, H=1080):
    """img float32 hxwx3, d Tiefe (1=nah), u in [0,1] → Frame W x H.
    Kamera bewegt sich: Grundfahrt (Zoom/Pan) + tiefenabhängige Verschiebung (Parallaxe)."""
    m = MOVES[move] if isinstance(move, str) else move
    e = u*u*(3-2*u)
    h, w = d.shape
    z = m["z0"]+(m["z1"]-m["z0"])*e
    gx, gy = np.meshgrid(np.arange(W, dtype=np.float32), np.arange(H, dtype=np.float32))
    # Grundabbildung (ohne Parallaxe), Bildmitte fest
    X = w/2 + (gx-W/2)*w/(W*z); Y = h/2 + (gy-H/2)*h/(H*z)
    dd = cv2.remap(d, X, Y, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)-0.35   # Hintergrund ~fest
    s = (e-0.5)
    # seitliche Kamerafahrt: nahe Dinge wandern stärker gegen die Fahrtrichtung
    X = X - dd*m["dx"]*w*s*2 - m["dx"]*w*s*0.3
    Y = Y - dd*m["dy"]*w*s*2 - m["dy"]*w*s*0.3
    # Dolly: nahe Dinge wachsen beim push schneller als der Hintergrund
    dz = (m["z1"]-m["z0"])*m["par"]*14*e*dd
    X = w/2 + (X-w/2)/(1+dz); Y = h/2 + (Y-h/2)/(1+dz)
    return cv2.remap(img, X, Y, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)

if __name__ == "__main__":
    cmd = sys.argv[1]
    im = cv2.imread(sys.argv[2])[..., ::-1].copy()
    if cmd == "depth":
        cv2.imwrite(sys.argv[3], (depth(im)*65535).astype(np.uint16))
    elif cmd == "test":
        out = sys.argv[3]; move = sys.argv[4] if len(sys.argv) > 4 else "push"; sec = float(sys.argv[5]) if len(sys.argv) > 5 else 5
        d = load_depth(sys.argv[2].rsplit(".", 1)[0]+"_depth.png", im)
        import subprocess
        p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "1920x1080", "-r", "24", "-i", "-",
                              "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
        f = im.astype(np.float32); n = int(sec*24)
        for i in range(n): p.stdin.write(np.clip(frame(f, d, i/(n-1), move), 0, 255).astype(np.uint8).tobytes())
        p.stdin.close(); p.wait()

# ---------- Atmosphäre: Regen, Staub, Licht-Flackern (kostenlos, prozedural) ----------
class Atmo:
    def __init__(self, kind, W=1920, H=1080, seed=3, n=None):
        r = np.random.default_rng(seed); self.k, self.W, self.H = kind, W, H
        n = n or {"rain": 420, "dust": 140, "snow": 220}.get(kind, 0)
        self.x = r.uniform(0, W, n); self.y = r.uniform(0, H, n); self.z = r.uniform(0.15, 1, n)
        self.ph = r.uniform(0, 6.28, n)
    def apply(self, fr, t):
        if self.k not in ("rain", "dust", "snow"): return fr
        layer = np.zeros((self.H, self.W), np.float32)
        if self.k == "rain":
            y = (self.y + t*(900+1400*self.z)) % (self.H+80) - 40; x = (self.x + t*120*self.z) % self.W
            for xi, yi, zi in zip(x, y, self.z):
                L = 18+50*zi; cv2.line(layer, (int(xi), int(yi)), (int(xi+L*0.12), int(yi+L)), 0.25+0.55*zi, 1+int(zi*1.6), cv2.LINE_AA)
            layer = cv2.GaussianBlur(layer, (0, 0), 0.8)
            return np.clip(fr*(1-0.06*layer[..., None]) + layer[..., None]*np.array([150, 165, 190], np.float32)*0.55, 0, 255)
        if self.k in ("dust", "snow"):
            sp = 18 if self.k == "dust" else 90
            y = (self.y + t*sp*(0.3+self.z)) % self.H; x = (self.x + 14*np.sin(t*0.5+self.ph)) % self.W
            for xi, yi, zi, p in zip(x, y, self.z, self.ph):
                a = (0.35+0.65*zi)*(0.6+0.4*np.sin(t*1.7+p)); cv2.circle(layer, (int(xi), int(yi)), 1+int(zi*2.5), a, -1, cv2.LINE_AA)
            layer = cv2.GaussianBlur(layer, (0, 0), 1.6)
            return np.clip(fr + layer[..., None]*np.array([255, 225, 185], np.float32)*0.5, 0, 255)

def flicker(fr, t, amt=0.06, seed=1):
    """leichtes Neon-/Lampen-Flackern auf hellen Stellen"""
    r = np.random.default_rng(int(t*24)+seed*1000).uniform()
    g = 1 - amt*(r > 0.92)*0.8 - amt*0.25*np.sin(t*11)
    lum = fr.mean(axis=2, keepdims=True)/255
    return np.clip(fr*(1-lum) + fr*lum*g, 0, 255)
