"""3D-Diorama-Effekte für Goldsmith (spec-Kinds, siehe effects.py):

  ["earthzoom", anchor, {"map": "map.png", "pin": [0.62, 0.2], "label": ["AGORDO, ITALY", "1961"],
                         "aerial": "dio/aerial", "room": "dio/workshop", "dur": "scene"}]
      Earth Zoom: Karte auf dem Ermittlertisch -> roter Pin -> Flug durch Wolken -> Luftaufnahme sinkt bis vors
      Fenster -> warmes Aufblenden -> Innenraum-Szene. "room" optional. map: Datei in a/ (Repo assets/img) oder img/.
      pin = Position auf der Karte (Anteile 0..1 des Kartenbildes).

  ["dio", anchor, {"clip": "dio/street", "caption": "NEW YORK · 2001", "stamp": "WITNESSED", "dur": "scene",
                   "post": {"focus": 0.5}, "amb": "amb_street"}]
      Polaroid-Zoom: Pinnwand mit Polaroid -> Kamera fährt ins Foto -> Foto wird lebendig (3D-Szene) ->
      am Ende friert das Bild ein, wird wieder Polaroid, Stempel. "stamp" optional ("" = ohne Rückweg-Stempel).

Clips = Ordner mit Blender-Frames f_####.png + meta.json (engine/diorama), Pfad relativ zum Arbeitsordner v3/.
"dur": Sekunden oder "scene" (= bis Szenenende). Die Clips laufen in Echtzeit (24 fps); ist die Szene länger,
wird der Clip leicht verlangsamt (min. 0.65x) und hält dann das letzte Bild.
Sound: nur Geräusche, die man sieht – die Blender-Szene hängt sie an Objekte (dio.sound, automatisch bei drive/walk),
cues.py mischt sie nach Entfernung/Bildposition. Raumklang ("amb", optional) nur sehr leise. Polaroid: Kamera-Klick rein,
Stempel raus. Musik wird in 3D-Szenen leicht abgesenkt (meta "ducks").
"""
import os, sys, math, numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "diorama"))
for _p in ("diorama", "../diorama"):
    if os.path.isdir(_p) and _p not in sys.path: sys.path.insert(0, _p)
import post as P

W, H = 1920, 1080
CLIP_FPS = 24
F = os.path.expanduser("~/.fonts"); TYPE = f"{F}/SpecialElite.ttf"; ANTON = f"{F}/Anton.ttf"
RED = (205, 25, 35); INK = (28, 22, 18); IVORY = (242, 234, 216)
_C = {}; _PP = {}


def ease(s): s = min(max(s, 0), 1); return s*s*(3-2*s)
def eout(s): s = min(max(s, 0), 1); return 1-(1-s)**3
def ein(s): s = min(max(s, 0), 1); return s**3
def font(p, s):
    k = (p, int(s))
    if k not in _C: _C[k] = ImageFont.truetype(p, int(s))
    return _C[k]


def view(img, cx, cy, z):
    ih, iw = img.shape[:2]; cw = iw/z; ch = cw*H/W
    x0 = cx*iw-cw/2; y0 = cy*ih-ch/2; sc = W/cw
    if z >= 1:   # im Bild bleiben (keine gespiegelten Ränder)
        x0 = min(max(x0, 0), iw-cw); y0 = min(max(y0, 0), ih-ch)
    M = np.float32([[sc, 0, -x0*sc], [0, sc, -y0*sc]])
    return cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)


def clip_dur(clip):
    return P.nframes(clip)/CLIP_FPS


def clip_frame(clip, lt, need, post=None):
    """Clip-Frame zur lokalen Zeit lt; need = wie lange der Clip insgesamt zu sehen ist."""
    cd = clip_dur(clip); rate = 1.0 if need <= cd else max(0.65, cd/need)
    idx = min(P.nframes(clip), 1+int(lt*rate*CLIP_FPS))
    k = (clip, idx, str(post))
    if k not in _PP:
        if len(_PP) > 6: _PP.clear()
        _PP[k] = P.frame(clip, idx, post or {})
    return _PP[k]


def typed_label(layer, lt, lines, xy, size=54, cps=16):
    d = ImageDraw.Draw(layer); f = font(TYPE, size); n = int(max(0, lt)*cps); y = xy[1]
    for ln in lines:
        vis = ln[:max(0, n)]; n -= len(ln)
        if vis:
            tw = d.textlength(ln, font=f)
            d.rectangle([xy[0]-18, y-10, xy[0]+tw+18, y+size+12], fill=(240, 232, 210, 235))
            d.text((xy[0], y), vis, font=f, fill=INK)
        y += size+30


def stamp_img(text, size=150, rot=-9):
    f = font(ANTON, size); tw = int(ImageDraw.Draw(Image.new("L", (1, 1))).textlength(text, font=f))
    st = Image.new("RGBA", (tw+120, int(size*1.75)), (0, 0, 0, 0)); sd = ImageDraw.Draw(st)
    sd.rounded_rectangle([14, 14, st.width-14, st.height-14], radius=18, outline=RED, width=max(8, size//12))
    sd.text((st.width/2, st.height/2), text, font=f, fill=RED, anchor="mm")
    a = np.array(st.getchannel("A")).astype(np.float32); rng = np.random.default_rng(len(text))
    a *= np.clip((cv2.GaussianBlur(rng.random(a.shape).astype(np.float32), (0, 0), 2.2)-0.36)*6, 0.25, 1)
    st.putalpha(Image.fromarray(a.astype(np.uint8))); return st.rotate(rot, expand=True, resample=Image.BICUBIC)


def stamp(layer, lt, text, center, size=150):
    if lt < 0 or not text: return
    k = ("stamp", text, size)
    if k not in _C: _C[k] = stamp_img(text, size)
    st = _C[k]; p = eout(lt/0.11); s = 2.0-p
    im = st.resize((int(st.width*s), int(st.height*s)), Image.BILINEAR)
    im.putalpha(im.getchannel("A").point(lambda v: int(v*0.93*min(1, p*1.3))))
    layer.alpha_composite(im, (int(center[0]-im.width/2), int(center[1]-im.height/2)))


def clouds(seed=3, size=1400):
    k = ("clouds", seed)
    if k not in _C:
        rng = np.random.default_rng(seed); a = np.zeros((size, size), np.float32)
        for sc, w in [(220, 0.55), (90, 0.3), (35, 0.15)]:
            n = rng.random((size//sc+3, size//sc+3)).astype(np.float32)
            a += w*cv2.resize(n, (size+3*sc, size+3*sc), interpolation=cv2.INTER_CUBIC)[:size, :size]
        a = np.clip((a-0.5)*3.2, 0, 1); a = cv2.GaussianBlur(a, (0, 0), 6)
        yy, xx = np.mgrid[0:size, 0:size]; r = np.hypot(xx-size/2, yy-size/2)/(size/2)
        a *= np.clip(r*1.6-0.25, 0, 1)       # Loch in der Mitte: wir fliegen hindurch
        _C[k] = a
    return _C[k]


def cloud_pass(fr, s, alpha, tint=(235, 228, 222)):
    """Wolkenschicht, die mit wachsendem s am Betrachter vorbeizieht."""
    if alpha <= 0.01: return fr
    out = fr.astype(np.float32)
    for i, (k, sp) in enumerate([(3, 1.0), (7, 1.55)]):
        a = clouds(k); sz = int(W*(0.7+2.6*s*sp)); sz = max(8, min(sz, 7000))
        if sz < W*0.6: continue
        big = cv2.resize(a, (sz, int(sz*1.0)), interpolation=cv2.INTER_LINEAR)
        x0 = (sz-W)//2; y0 = (sz-H)//2
        if x0 < 0 or y0 < 0: continue
        m = big[y0:y0+H, x0:x0+W][..., None]*alpha*(1 if i == 0 else 0.7)
        out = out*(1-m) + np.array(tint, np.float32)*m
    return out.astype(np.uint8)


def warm_flash(fr, k):
    if k <= 0: return fr
    return np.clip(fr.astype(np.float32)*(1+0.6*k) + np.array([255, 196, 120], np.float32)*k*0.9, 0, 255).astype(np.uint8)


# ======================================================================== Earth Zoom
A_DUR = 2.6     # Kartenphase


def earthzoom(t, T, p, ctx):
    a_dir = ctx["a"]; mp = p.get("map", "map.png")
    mpath = f"{ctx['img']}/{mp}" if os.path.exists(f"{ctx['img']}/{mp}") else f"{a_dir}/{mp}"
    if ("ezmap", mpath) not in _C:
        im = cv2.cvtColor(cv2.imread(mpath), cv2.COLOR_BGR2RGB)
        _C[("ezmap", mpath)] = cv2.resize(im, (im.shape[1]*2, im.shape[0]*2), interpolation=cv2.INTER_CUBIC)
    MAP = _C[("ezmap", mpath)]; px, py = p.get("pin", [0.5, 0.4]); layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    aerial = p["aerial"]; room = p.get("room")
    ta = clip_dur(aerial)
    post_a = dict({"focus": 0.5, "band": 0.12, "blur": 12, "dust": 0, "warm": 0.35}, **p.get("post_aerial", {}))
    post_r = dict({"focus": 0.45, "band": 0.14}, **p.get("post", {}))
    if t < A_DUR:
        # 1) Karte: kurzer Halt, Pin fällt, Ort wird getippt, dann exponentieller Zoom in den Pin
        z = 1.0 if t < 1.1 else 1.0*math.exp(ein((t-1.1)/(A_DUR-1.1))*3.0)
        cx = 0.5+(px-0.5)*ease((t-0.2)/1.4); cy = 0.5+(py-0.5)*ease((t-0.2)/1.4)
        fr = view(MAP, cx, cy, z)
        ih, iw = MAP.shape[:2]; cw = iw/z; chh = cw*H/W
        ox = min(max(cx*iw-cw/2, 0), iw-cw); oy = min(max(cy*ih-chh/2, 0), ih-chh)
        pxs = (px*iw-ox)*W/cw; pys = (py*ih-oy)*W/cw
        pin_a = 1.0 - ease((t-1.5)/0.6)   # Pin verblasst, bevor wir in die Wolken tauchen
        if t > 0.3 and pin_a > 0.01:
            pl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            d = ImageDraw.Draw(pl); pr = eout((t-0.3)/0.3); yo = -220*(1-pr); r = 22
            for k in range(2):
                rr = t-0.6-k*0.4
                if 0 < rr < 1.1:
                    rad = 20+150*eout(rr/1.1); al = int(200*(1-rr/1.1))
                    d.ellipse([pxs-rad, pys-rad*0.5, pxs+rad, pys+rad*0.5], outline=(220, 30, 40, al), width=5)
            d.line([(pxs, pys+yo), (pxs+9, pys-44+yo)], fill=(180, 180, 185, 255), width=5)
            d.ellipse([pxs+13-r, pys-58+yo-r, pxs+13+r, pys-58+yo+r], fill=(210, 25, 35, 255), outline=(90, 0, 0, 255), width=3)
            d.ellipse([pxs+3, pys-72+yo, pxs+12, pys-63+yo], fill=(255, 140, 140, 255))
            if pin_a < 1: pl.putalpha(pl.getchannel("A").point(lambda v: int(v*pin_a)))
            layer.alpha_composite(pl)
        if 0.6 < t < A_DUR-0.5 and p.get("label"):
            al = 1.0 if t < A_DUR-0.8 else (A_DUR-0.5-t)/0.3
            lab = Image.new("RGBA", (W, H), (0, 0, 0, 0)); typed_label(lab, t-0.6, p["label"], (min(W-620, pxs+60), max(60, pys-40)))
            if al < 1: lab.putalpha(lab.getchannel("A").point(lambda v: int(v*max(0, al))))
            layer.alpha_composite(lab)
        k = ease((t-1.6)/(A_DUR-1.6))
        fr = cloud_pass(fr, k*0.6, k*0.9)
        if t > A_DUR-0.35:   # Übergang in die Luftaufnahme
            f2 = clip_frame(aerial, 0, ta, post_a); m = ease((t-(A_DUR-0.35))/0.35)
            fr = (fr*(1-m)+cloud_pass(f2, 0.6+m*0.4, 0.9)*m).astype(np.uint8)
        return fr, layer
    lt = t - A_DUR
    room_need = T - A_DUR - ta
    if lt < ta or not room:
        fr = clip_frame(aerial, lt, ta, post_a)
        if lt < 1.4: fr = cloud_pass(fr, 1.0+lt*1.2, 0.9*(1-ease(lt/1.4)))
        if room and lt > ta-0.45: fr = warm_flash(fr, ease((lt-(ta-0.45))/0.45))
        return fr, layer
    lr = lt - ta
    fr = clip_frame(room, lr, max(room_need, 0.1), post_r)
    if lr < 0.5: fr = warm_flash(fr, 1-ease(lr/0.5))
    return fr, layer


def clip_rate(clip, need):
    cd = clip_dur(clip); return 1.0 if need <= cd else max(0.65, cd/need)


def cue_event(t, clip, need, gain=1.0):
    """Objekt-Geräusche des Clips (Auto, Schritte, Tür …) als eine Spur; Tempo folgt dem Clip."""
    try:
        import cues as CU
        sfx = "sfx" if os.path.isdir("sfx") else os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "sfx")
        path = CU.build(clip, sfx)
    except Exception as e:
        print("Cues nicht gebaut:", clip, e); return []
    return [(t, f"clip:{os.path.abspath(path)}:{clip_rate(clip, need):.3f}", gain)]


def earthzoom_sounds(p, dur):
    """Pin + leiser Hit, dann nur Geräusche, die man sieht (Auto, Schritte …), Raumklang sehr leise.
    Kein Wind/Rauschen (Laurin 16.11.2026)."""
    ta = clip_dur(p["aerial"]); ev = [(0.3, "pin", 0.8)]
    # Reinzoomen hörbar machen (Laurin 17.11.): Riser beim Abtauchen, Whoosh beim Durchstoßen, zweiter Whoosh in den Raum
    ev += [(0.9, "riser", 0.4), (A_DUR-0.45, "whoosh", 0.85)]
    if p.get("room"): ev += [(A_DUR+ta-0.35, "whoosh", 0.55)]
    ev += cue_event(A_DUR, p["aerial"], ta)
    if p.get("amb_aerial"): ev += [(A_DUR+0.2, f"amb:{p['amb_aerial']}:{max(0.5, ta-0.2):.2f}", 0.25)]
    if p.get("room"):
        rn = max(0.1, dur-A_DUR-ta)
        ev += [(A_DUR+ta-0.05, "sub_drop", 0.45)] + cue_event(A_DUR+ta, p["room"], rn)
        if p.get("amb"): ev += [(A_DUR+ta, f"amb:{p['amb']}:{max(0.5, rn):.2f}", 0.3)]
    return ev


# ======================================================================== Polaroid-Zoom
IN_DUR = 1.5; OUT_DUR = 1.1


def board_with_polaroid(clip, p, ctx):
    """Großes Pinnwand-Bild (2x) mit Polaroid (Foto = verblichener erster Frame) + roter Faden."""
    k = ("board", clip, p.get("caption"))
    if k in _C: return _C[k]
    BW, BH = W*2, H*2
    board = Image.open(f"{ctx['a']}/board.png").convert("RGB").resize((BW, BH), Image.LANCZOS).convert("RGBA")
    photo = clip_frame(clip, 0, 1, dict({"focus": 0.5}, **p.get("post", {})))
    ph = Image.fromarray(faded(photo)).resize((1440, 810), Image.LANCZOS)
    pw, phh = ph.width+90, ph.height+250
    pol = Image.new("RGBA", (pw, phh), (238, 233, 220, 255)); pol.paste(ph, (45, 45))
    d = ImageDraw.Draw(pol)
    if p.get("caption"): d.text((pw/2, ph.height+45+105), p["caption"], font=font(TYPE, 74), fill=(40, 34, 30), anchor="mm")
    rot = p.get("rot", -2.5); polr = pol.rotate(rot, expand=True, resample=Image.BICUBIC)
    cx, cy = BW*0.5, BH*0.47; x0, y0 = int(cx-polr.width/2), int(cy-polr.height/2)
    sh = Image.new("RGBA", (BW, BH), (0, 0, 0, 0)); ImageDraw.Draw(sh).rectangle([x0+30, y0+40, x0+polr.width+30, y0+polr.height+40], fill=(0, 0, 0, 170))
    board.alpha_composite(sh.filter(ImageFilter.GaussianBlur(30))); board.alpha_composite(polr, (x0, y0))
    d = ImageDraw.Draw(board)
    d.line([(cx-40, y0+30), (BW*0.02, BH*0.18)], fill=(190, 20, 30, 255), width=9); d.line([(cx+40, y0+30), (BW*0.98, BH*0.3)], fill=(190, 20, 30, 255), width=9)
    d.ellipse([cx-34, y0+2, cx+34, y0+70], fill=(205, 25, 35, 255), outline=(90, 0, 0, 255), width=4)
    # Fotobereich im Board (für den Zoom): Mittelpunkt + Breite (Rotation vernachlässigbar)
    a = math.radians(-rot); ox, oy = 0, -(phh/2-45-ph.height/2)
    fx, fy = cx+ox*math.cos(a)-oy*math.sin(a), cy+ox*math.sin(a)+oy*math.cos(a)
    _C[k] = (np.asarray(board.convert("RGB")), (fx/BW, fy/BH, ph.width/BW), rot)
    return _C[k]


def faded(fr):
    x = fr.astype(np.float32); g = x.mean(2, keepdims=True); x = g+(x-g)*0.55
    x = x*np.array([1.05, 0.98, 0.86])+np.array([18, 12, 4]); return np.clip(x, 0, 255).astype(np.uint8)


def rot_img(fr, ang, z):
    M = cv2.getRotationMatrix2D((W/2, H/2), ang, z); return cv2.warpAffine(fr, M, (W, H), borderMode=cv2.BORDER_REFLECT)


def dio(t, T, p, ctx):
    clip = p["clip"]; post = dict({"focus": 0.5}, **p.get("post", {}))
    BOARD, (fx, fy, fw), rot = board_with_polaroid(clip, p, ctx)
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    z_fill = 1.0/fw*1.02
    back = bool(p.get("stamp", "CASE FILE")) and T > IN_DUR+OUT_DUR+1.0
    t_out = T-OUT_DUR if back else T+1
    need = (t_out if back else T)-IN_DUR+0.4
    if t < IN_DUR:
        # Kamera fährt von der Pinnwand ins Foto; Foto färbt sich ein und wird lebendig
        s = ease(t/IN_DUR); z = 1.15*(z_fill/1.15)**(s**1.4)
        cx = 0.5+(fx-0.5)*s; cy = 0.48+(fy-0.48)*s
        fr = view(BOARD, cx, cy, z); fr = rot_img(fr, -rot*s, 1.0)
        if t > IN_DUR-0.55:
            m = ease((t-(IN_DUR-0.55))/0.55); live = clip_frame(clip, 0, need, post)
            liv = (faded(live)*(1-m)+live*m).astype(np.uint8) if m < 1 else live
            k = ease((t-(IN_DUR-0.55))/0.3); fr = (fr*(1-k)+liv*k).astype(np.uint8)
        return fr, layer
    if t < t_out:
        return clip_frame(clip, t-IN_DUR+0.0, need, post), layer
    # Rückweg: einfrieren, verblassen zum Polaroid, Kamera zieht zurück, Stempel
    lt = t-t_out; s = 1-ease(lt/0.8)
    frozen = clip_frame(clip, t_out-IN_DUR, need, post)
    z = 1.15*(z_fill/1.15)**(s**1.4); cx = 0.5+(fx-0.5)*s; cy = 0.48+(fy-0.48)*s
    m = ease(lt/0.35)
    if s > 0.97:
        fr = (frozen*(1-m)+faded(frozen)*m).astype(np.uint8)
    else:
        fr = rot_img(view(BOARD, cx, cy, z), -rot*s, 1.0)
        if s > 0.85: fr = (fr*(1-(s-0.85)/0.15)+faded(frozen)*((s-0.85)/0.15)).astype(np.uint8)
    stamp(layer, lt-0.75, p.get("stamp", "CASE FILE"), (W*0.66, H*0.62))
    return fr, layer


def dio_sounds(p, dur):
    back = bool(p.get("stamp", "CASE FILE")) and dur > IN_DUR+OUT_DUR+1.0
    need = (dur-OUT_DUR if back else dur)-IN_DUR+0.4
    ev = [(IN_DUR-0.6, "shutter", 0.55), (IN_DUR-0.45, "whoosh", 0.6)] + cue_event(IN_DUR, p["clip"], need)
    if p.get("amb"): ev += [(IN_DUR-0.2, f"amb:{p['amb']}:{max(0.5, dur-IN_DUR-0.2):.2f}", 0.3)]
    if p.get("stamp", "CASE FILE") and dur > IN_DUR+OUT_DUR+1.0: ev += [(dur-OUT_DUR+0.75, "stamp", 0.9)]
    return ev
