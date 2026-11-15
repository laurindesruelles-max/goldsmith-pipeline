import subprocess, json, os, sys, random, math, numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1920, 1080, 30
HOME = os.path.expanduser("~")
F_ANTON = f"{HOME}/.fonts/Anton.ttf"; F_SERIF = f"{HOME}/.fonts/playfair-display-latin-700-normal.ttf"
F_SERIF4 = f"{HOME}/.fonts/playfair-display-latin-400-normal.ttf"
F_TYPE = f"{HOME}/.fonts/SpecialElite.ttf"; F_SANS = "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf"
GOLD = (222, 188, 104); IVORY = (242, 234, 216); RED = (200, 30, 40); INK = (30, 24, 20)
FONT = {}
def font(p, s):
    k = (p, int(s))
    if k not in FONT: FONT[k] = ImageFont.truetype(p, int(s))
    return FONT[k]

def dur(f): return float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",f]))
A = lambda n: f"../audio/{n}.wav"
PAD = {6: 0.95, 8: 0.35}
PLAN = [(n, round((dur(A(n)) + PAD.get(n, 0.35))*FPS)/FPS) for n in range(1, 9)]
S0 = {}; acc = 0
for n, T in PLAN: S0[n] = acc; acc += T
TOTAL = acc

def ease(s): s = min(max(s, 0), 1); return s*s*(3-2*s)
def eout(s): s = min(max(s, 0), 1); return 1-(1-s)**3

# ---------- camera ----------
def view(img, cx, cy, z, dx=0, dy=0, rot=0):
    ih, iw = img.shape[:2]; cw = iw/z; ch = cw*H/W
    if ch > ih: ch = ih; cw = ch*W/H
    x0 = min(max(cx*iw-cw/2, 0), iw-cw); y0 = min(max(cy*ih-ch/2, 0), ih-ch)
    sc = W/cw
    M = np.float32([[sc, 0, -x0*sc+dx], [0, sc, -y0*sc+dy]])
    if rot:
        R = cv2.getRotationMatrix2D((W/2, H/2), rot, 1.0); M = (np.vstack([R, [0,0,1]]) @ np.vstack([M, [0,0,1]]))[:2].astype(np.float32)
    return cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
def cam(keys, t):
    """keys: list of (t_arrive, (cx,cy,z), move_dur). camera arrives at value at t_arrive."""
    v = keys[0][1]
    for ta, val, md in keys[1:]:
        if t >= ta: v = val
        elif t > ta-md:
            s = ease((t-(ta-md))/md); return tuple(a+(b-a)*s for a, b in zip(v, val))
        else: break
    return v
def shake(t, t0, amp=18, d=0.45):
    if t < t0 or t > t0+d: return 0, 0
    k = (1-(t-t0)/d)**2; return amp*k*math.sin(t*93), amp*k*math.cos(t*71)

def load_rgb(p, w=W, h=H):
    return cv2.resize(cv2.cvtColor(cv2.imread(p), cv2.COLOR_BGR2RGB), (w, h), interpolation=cv2.INTER_CUBIC)
def rgba_over(frame, layer):
    arr = np.asarray(layer); a = arr[..., 3:4]
    if not a.any(): return frame
    a = a.astype(np.float32)/255.0
    return (frame*(1-a) + arr[..., :3]*a).astype(np.uint8)

# ---------- text helpers ----------
def shadow_text(img, xy, text, f, fill, stroke=0, blur=8, anchor="la", alpha=255):
    sh = Image.new("RGBA", img.size, (0,0,0,0)); ImageDraw.Draw(sh).text((xy[0]+5, xy[1]+7), text, font=f, fill=(0,0,0,int(220*alpha/255)), anchor=anchor, features=["lnum"])
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(blur)))
    ImageDraw.Draw(img).text(xy, text, font=f, fill=fill[:3]+(alpha,), anchor=anchor, stroke_width=stroke, stroke_fill=(0,0,0,alpha), features=["lnum"])

def typed(layer, t, t0, lines, xy, size=64, cps=15, box=True, color=IVORY, cursor=True):
    if t < t0: return
    f = font(F_TYPE, size); d = ImageDraw.Draw(layer); x, y = xy
    n = int((t-t0)*cps); k = 0
    if box:
        maxw = max(d.textlength(l, font=f) for l in lines)
        b = Image.new("RGBA", layer.size, (0,0,0,0))
        ImageDraw.Draw(b).rectangle([x-30, y-24, x+maxw+60, y+len(lines)*(size+18)+10], fill=(10,10,12,185)); layer.alpha_composite(b)
    for li, line in enumerate(lines):
        vis = line[:max(0, min(len(line), n-k))]
        d.text((x, y+li*(size+18)), vis, font=f, fill=color)
        if cursor and 0 <= n-k <= len(line) and int(t*2.5) % 2 == 0:
            cx = x + d.textlength(vis, font=f) + 6; d.rectangle([cx, y+li*(size+18)+8, cx+size*0.45, y+li*(size+18)+size], fill=GOLD)
        k += len(line)+4
def typed_sfx(ev, t0, lines, cps=15, gain=0.5):
    k = 0
    for line in lines:
        for ch in line:
            if ch != " ": ev.append((t0+k/cps, f"key{random.randint(0,3)}", gain))
            k += 1
        k += 4

def pop_word(layer, t, t0, text, color=(255,255,255), y=900, size=140, t1=None):
    if t < t0 or (t1 and t > t1): return
    p = eout((t-t0)/0.16); s = 0.55+0.45*p
    a = 255 if not t1 else int(255*min(1, (t1-t)/0.12))
    shadow_text(layer, (W/2, y), text, font(F_ANTON, size*s), color, stroke=7, anchor="mm", alpha=a)

def chapter(layer, t, t0, label):
    if t < t0: return
    a = ease((t-t0)/0.4); f = font(F_SANS, 30); d = ImageDraw.Draw(layer)
    tw = d.textlength(label, font=f); w = int((tw+70)*eout((t-t0)/0.35))
    if w <= 0: return
    layer.alpha_composite(Image.new("RGBA", (w, 70), (8,9,12,int(210*a))), (90, 90))
    d.rectangle([90, 90, 98, 160], fill=RED+(255,))
    if t > t0+0.25: d.text((122, 106), label, font=f, fill=IVORY+(int(255*ease((t-t0-0.25)/0.3)),))

def stamp_img(text, size=170, color=(205,25,35), rot=-8):
    f = font(F_ANTON, size); tw = int(ImageDraw.Draw(Image.new("L", (1,1))).textlength(text, font=f))
    st = Image.new("RGBA", (tw+120, int(size*1.75)), (0,0,0,0)); sd = ImageDraw.Draw(st)
    sd.rounded_rectangle([14, 14, st.width-14, st.height-14], radius=18, outline=color, width=max(8, size//12))
    sd.text((st.width/2, st.height/2), text, font=f, fill=color, anchor="mm")
    # grunge: knock out random specks
    a = np.array(st.getchannel("A")).astype(np.float32); rng = np.random.default_rng(len(text))
    noise = cv2.GaussianBlur(rng.random(a.shape).astype(np.float32), (0,0), 2.2)
    a *= np.clip((noise-0.36)*6, 0.25, 1); st.putalpha(Image.fromarray(a.astype(np.uint8)))
    return st.rotate(rot, expand=True, resample=Image.BICUBIC)
STAMPS = {}
def stamp(layer, t, t0, text, center, size=170, rot=-8, color=(205,25,35)):
    if t < t0: return
    k = (text, size, rot, color)
    if k not in STAMPS: STAMPS[k] = stamp_img(text, size, color, rot)
    st = STAMPS[k]; p = eout((t-t0)/0.11); s = 2.0-1.0*p
    im = st.resize((int(st.width*s), int(st.height*s)), Image.BILINEAR)
    im.putalpha(im.getchannel("A").point(lambda v: int(v*0.93*min(1, p*1.3))))
    layer.alpha_composite(im, (int(center[0]-im.width/2), int(center[1]-im.height/2)))

# ---------- props ----------
CS = 1.5  # board canvas scale
CW, CH = int(W*CS), int(H*CS)
def polaroid(path, caption, w=500, rot=0):
    ph = Image.open(path).convert("RGB").resize((w-50, w-50), Image.LANCZOS)
    fr = Image.new("RGBA", (w, w+70), (238,233,222,255)); fr.paste(ph, (25, 25))
    d = ImageDraw.Draw(fr); d.text((w/2, w+18), caption, font=font(F_TYPE, 48), fill=INK, anchor="mm")
    tape = Image.new("RGBA", (170, 54), (226,214,170,170)); fr.alpha_composite(tape, (w//2-85, -14 if False else 0))
    pad = 60; c = Image.new("RGBA", (w+2*pad, w+70+2*pad), (0,0,0,0))
    sh = Image.new("RGBA", c.size, (0,0,0,0)); ImageDraw.Draw(sh).rectangle([pad+10, pad+16, pad+w+10, pad+w+86], fill=(0,0,0,170))
    c.alpha_composite(sh.filter(ImageFilter.GaussianBlur(14))); c.alpha_composite(fr, (pad, pad))
    return c.rotate(rot, expand=False, resample=Image.BICUBIC)
def tag(text):
    f = font(F_TYPE, 58); w = int(ImageDraw.Draw(Image.new("L", (1,1))).textlength(text, font=f))+70
    im = Image.new("RGBA", (w+40, 140), (0,0,0,0)); d = ImageDraw.Draw(im)
    d.polygon([(20,30),(w-10,30),(w+20,70),(w-10,110),(20,110)], fill=(245,240,228,255))
    d.ellipse([w-18, 62, w-2, 78], fill=(60,50,40,255)); d.text((45, 70), text, font=f, fill=(170,20,28), anchor="lm")
    sh = Image.new("RGBA", im.size, (0,0,0,0)); sh.alpha_composite(im); a = sh.getchannel("A").point(lambda v: int(v*0.6))
    shd = Image.new("RGBA", im.size, (0,0,0,0)); shd.putalpha(a); shd = shd.filter(ImageFilter.GaussianBlur(6))
    out = Image.new("RGBA", (im.width+20, im.height+20), (0,0,0,0)); out.alpha_composite(shd, (12, 14)); out.alpha_composite(im, (0, 0))
    return out.rotate(random.Random(text).uniform(-10, 10), expand=True, resample=Image.BICUBIC)

BOARD = None; ITEMS = []; STR_SRC = []; CENTER = (0.5*CW, 0.52*CH)
def init_board():
    global BOARD, ITEMS, STR_SRC
    BOARD = Image.open("a/board.png").convert("RGBA").resize((CW, CH), Image.LANCZOS)
    s1, s2 = S0[1], S0[2]
    P = [("a/g_aviator.png", "RAY-BAN", (0.25, 0.30), -6, s1+3.77), ("a/g_sport.png", "OAKLEY", (0.50, 0.28), 4, s1+5.90),
         ("a/g_luxury.png", "PRADA", (0.75, 0.31), -3, s1+8.78), ("a/g_round.png", "PERSOL", (0.36, 0.71), 5, s2+0.35),
         ("a/g_cateye.png", "MIU MIU", (0.64, 0.71), -5, s2+0.95)]
    ITEMS = []
    for p, cap, pos, r, t0 in P:
        im = polaroid(p, cap, rot=r); ITEMS.append((im, (pos[0]*CW, pos[1]*CH), t0, "slap"))
        STR_SRC.append((pos[0]*CW, pos[1]*CH - 255))
    for txt, pos, t0 in [("$39", (0.14, 0.50), s2+1.59), ("$189", (0.60, 0.47), s2+1.72), ("$420", (0.88, 0.52), s2+1.85)]:
        ITEMS.append((tag(txt), (pos[0]*CW, pos[1]*CH), t0, "slap"))
_cache = {}
def board_at(T):
    """board canvas at global time T (polaroids + strings)."""
    s3 = S0[3]; str_t = [s3+0.30+0.13*i for i in range(5)]
    settled = tuple(T >= t0+0.15 for _, _, t0, _ in ITEMS); strs = tuple(min(1, max(0, (T-ts)/0.28)) for ts in str_t)
    anim = any(t0 <= T < t0+0.15 for _, _, t0, _ in ITEMS) or any(0 < s < 1 for s in strs)
    key = (settled, strs)
    if not anim and key in _cache: return _cache[key]
    im = BOARD.copy()
    for (pim, (x, y), t0, kind) in ITEMS:
        if T < t0: continue
        p = eout((T-t0)/0.15); s = 1+0.45*(1-p)
        q = pim if s == 1 else pim.resize((int(pim.width*s), int(pim.height*s)), Image.BILINEAR)
        if p < 1: q.putalpha(q.getchannel("A").point(lambda v: int(v*min(1, p*2))))
        im.alpha_composite(q, (int(x-q.width/2), int(y-q.height/2)))
    d = ImageDraw.Draw(im)
    for (sx, sy), pr in zip(STR_SRC, strs):
        if pr <= 0: continue
        ex = sx+(CENTER[0]-sx)*pr; ey = sy+(CENTER[1]-sy)*pr
        d.line([(sx, sy), (ex, ey)], fill=(120,8,14), width=13); d.line([(sx, sy), (ex, ey)], fill=(205,22,32), width=8)
        d.ellipse([sx-15, sy-15, sx+15, sy+15], fill=(220,30,40), outline=(70,0,0), width=4)
    if any(s > 0 for s in strs):
        cx, cy = CENTER; d.ellipse([cx-24, cy-24, cx+24, cy+24], fill=(230,30,40), outline=(70,0,0), width=4)
    arr = np.asarray(im.convert("RGB"))
    if not anim: _cache.clear(); _cache[key] = arr
    return arr

def card_img(front=True, w=860, h=480):
    c = Image.new("RGBA", (w, h), (236,226,200,255) if front else (196,160,98,255)); d = ImageDraw.Draw(c)
    if front:
        for y in range(120, h-30, 46): d.line([(30, y), (w-30, y)], fill=(150,170,200,140), width=2)
        d.line([(30, 100), (w-30, 100)], fill=(200,60,60,200), width=3)
        d.text((w/2, 230), "ONE COMPANY.", font=font(F_ANTON, 150), fill=(165,18,26), anchor="mm")
    else:
        d.text((w/2, h/2), "EXHIBIT  A", font=font(F_TYPE, 70), fill=(110,80,40), anchor="mm")
    return c
CARD_F = None; CARD_B = None

def clipping():
    w, h = 980, 600
    c = Image.new("RGB", (w, h), (226,216,190)); arr = np.asarray(c).astype(np.int16)
    arr = np.clip(arr + np.random.default_rng(3).normal(0, 7, (h, w, 1)), 0, 255).astype(np.uint8); c = Image.fromarray(arr).convert("RGBA")
    d = ImageDraw.Draw(c)
    d.text((40, 30), "BUSINESS  ·  JUNE 2007", font=font(F_SANS, 26), fill=(60,50,40)); d.line([(40, 72), (w-40, 72)], fill=(40,30,25), width=3)
    d.text((40, 95), "LUXOTTICA TO BUY", font=font(F_SERIF, 84), fill=(25,20,18), features=["lnum"])
    d.text((40, 190), "RIVAL OAKLEY", font=font(F_SERIF, 84), fill=(25,20,18), features=["lnum"])
    d.text((40, 300), "$2.1 billion deal ends a bitter feud", font=font(F_SERIF4, 40), fill=(55,45,38), features=["lnum"])
    rng = random.Random(5)
    for col in range(3):
        for r in range(9):
            x0 = 40+col*305; y = 380+r*22; d.line([(x0, y), (x0+rng.randint(220, 280), y)], fill=(120,110,95), width=7)
    sh = Image.new("RGBA", (w+60, h+60), (0,0,0,0)); ImageDraw.Draw(sh).rectangle([30, 36, w+30, h+36], fill=(0,0,0,190))
    sh = sh.filter(ImageFilter.GaussianBlur(14)); sh.alpha_composite(c, (24, 24))
    return sh.rotate(3, expand=True, resample=Image.BICUBIC)

def pin_drop(layer, t, t0, pt):
    if t < t0-0.3: return
    p = eout((t-(t0-0.3))/0.3); x, y = pt; yo = -260*(1-p)
    d = ImageDraw.Draw(layer)
    if t >= t0:
        for k in range(2):
            r = (t-t0-k*0.35)
            if 0 < r < 1.2:
                rad = 20+180*eout(r/1.2); a = int(220*(1-r/1.2)); d.ellipse([x-rad, y-rad*0.45, x+rad, y+rad*0.45], outline=(220,30,40,a), width=6)
    sh = Image.new("RGBA", layer.size, (0,0,0,0)); ImageDraw.Draw(sh).ellipse([x-14, y-5, x+14, y+5], fill=(0,0,0,int(160*p)))
    layer.alpha_composite(sh.filter(ImageFilter.GaussianBlur(4)))
    d.line([(x, y+yo), (x+10, y-48+yo)], fill=(180,180,185,255), width=5)
    cx, cy = x+14, y-62+yo
    d.ellipse([cx-26, cy-26, cx+26, cy+26], fill=(210,25,35,255), outline=(90,0,0,255), width=3)
    d.ellipse([cx-12, cy-16, cx-2, cy-6], fill=(255,140,140,255))

# ---------- scenes ----------
IMG = {}
def frame(n, t, T):
    g = S0[n]+t; layer = Image.new("RGBA", (W, H), (0,0,0,0)); dx = dy = 0
    if n == 1:
        if t < 3.55:
            fr = view(IMG["desk"], *cam([(0, (0.62, 0.5, 1.15), 0), (3.55, (0.72, 0.45, 1.6), 3.4)], t))
            typed(layer, t, 0.25, ["CASE FILE #001", "SUBJECT: UNKNOWN"], (170, 760), size=70)
        else:
            c = cam([(0, (0.25, 0.32, 1.9), 0), (5.9, (0.5, 0.31, 1.9), 0.4), (8.78, (0.75, 0.33, 1.9), 0.4), (11.4, (0.5, 0.45, 1.3), 1.4)], t)
            for t0 in (3.77, 5.90, 8.78):
                sx, sy = shake(t, t0+0.1, 14, 0.3); dx += sx; dy += sy
            fr = view(board_at(g), *c, dx, dy)
            if 3.71 <= t < 3.77 or 5.84 <= t < 5.90 or 8.72 <= t < 8.78: fr = np.full_like(fr, 245)
    elif n == 2:
        c = cam([(0, (0.5, 0.45, 1.3), 0), (0.35, (0.36, 0.68, 1.75), 0.35), (0.95, (0.64, 0.68, 1.75), 0.35), (1.59, (0.55, 0.5, 1.25), 0.4), (4.21, (0.5, 0.5, 1.0), 0.6)], t)
        for t0 in (0.35, 0.95, 1.59, 1.72, 1.85):
            sx, sy = shake(t, t0+0.1, 10, 0.25); dx += sx; dy += sy
        fr = view(board_at(g), *c, dx, dy)
        for w, t0, t1 in [("DIFFERENT BRANDS.", 0.35, 1.5), ("DIFFERENT PRICES.", 1.59, 2.8), ("DIFFERENT STORES.", 2.87, 4.1)]:
            pop_word(layer, t, t0, w, t1=t1)
        pop_word(layer, t, 4.21, "IT FEELS LIKE CHOICE.", color=GOLD, size=125)
    elif n == 3:
        c = cam([(0, (0.5, 0.5, 1.0), 0), (T, (0.5, 0.51, 1.12), T)], t)
        dx, dy = shake(t, 0.25, 26, 0.6)
        fr = view(board_at(g), *c, dx, dy)
        if t < 0.35: fr = (fr.astype(np.float32)*(1+1.2*(1-t/0.35))).clip(0, 255).astype(np.uint8)
        if t >= 1.5:  # dim + card flip
            a = ease((t-1.5)/0.4); fr = (fr*(1-0.6*a)).astype(np.uint8)
            p = (t-1.68)/0.32
            if p >= 0:
                p = min(1, p); sx = abs(math.cos(p*math.pi)); im = CARD_B if p < 0.5 else CARD_F
                if p < 1: im = im.resize((max(2, int(im.width*sx)), im.height))
                s = 1.0+0.1*(1-eout((t-1.68)/0.6)); im = im.resize((int(im.width*s), int(im.height*s)))
                sh = Image.new("RGBA", (W, H), (0,0,0,0)); ImageDraw.Draw(sh).rectangle([W/2-im.width/2+14, H/2-im.height/2+22, W/2+im.width/2+14, H/2+im.height/2+22], fill=(0,0,0,200))
                layer.alpha_composite(sh.filter(ImageFilter.GaussianBlur(16))); layer.alpha_composite(im, (int(W/2-im.width/2), int(H/2-im.height/2)))
            if t >= 5.59:
                typed(layer, t, 5.59, ["NAME:"], (W/2-380, H/2+120), size=56, box=False, color=INK, cursor=False)
                if t >= 6.1:
                    p2 = eout((t-6.1)/0.15); d = ImageDraw.Draw(layer)
                    d.rectangle([W/2-200, H/2+118, W/2-200+560*p2, H/2+188], fill=(12,12,12,255))
                if t >= 6.6: stamp(layer, t, 6.6, "CLASSIFIED", (W/2+240, H/2-150), size=78, rot=10)
    elif n == 4:
        im = IMG["board4"].copy(); d = ImageDraw.Draw(im); sx, sy = W/1344, H/752
        PH = {"FACTORY": (273, 100, 350), "THE BRANDS": (1085, 100, 350), "THE STORES": (273, 450, 700), "THE INSURANCE": (1085, 478, 686)}
        PIN = (672*sx, 392*sy); starts = [0.25, 2.37, 4.62, 7.0]
        for (label, (px, py, pb)), t0 in zip(PH.items(), starts):
            if t < t0: continue
            p = eout((t-t0)/0.4); ex, ey = px*sx, py*sy
            x1 = PIN[0]+(ex-PIN[0])*p; y1 = PIN[1]+(ey-PIN[1])*p
            d.line([PIN, (x1, y1)], fill=(120,8,14), width=11); d.line([PIN, (x1, y1)], fill=(205,22,32), width=7)
            if p >= 1: d.ellipse([ex-13, ey-13, ex+13, ey+13], fill=(220,30,40), outline=(60,0,0), width=3)
        d.ellipse([PIN[0]-18, PIN[1]-18, PIN[0]+18, PIN[1]+18], fill=(230,30,40), outline=(60,0,0), width=3)
        # camera visits each target
        keys = [(0, (0.5, 0.5, 1.0), 0)]
        for (label, (px, py, pb)), t0 in zip(PH.items(), starts):
            keys.append((t0+0.5, ((px/1344+0.5)/2, (py/752+0.5)/2+0.08, 1.28), 0.5))
        keys.append((T-0.3, (0.5, 0.5, 1.0), 1.4))
        c = cam(keys, t)
        for t0 in starts:
            sx2, sy2 = shake(t, t0+0.4, 8, 0.25); dx += sx2; dy += sy2
        base = np.asarray(im.convert("RGB"))
        f = font(F_TYPE, 46); lab = Image.new("RGBA", (W, H), (0,0,0,0))
        for (label, (px, py, pb)), t0 in zip(PH.items(), starts):
            if t < t0+0.45: continue
            vis = label[:int((t-t0-0.45)*16)]; bx, by = px*sx, pb*sy-60
            ImageDraw.Draw(lab).rectangle([bx-175, by-32, bx+175, by+32], fill=(240,232,210,240))
            ImageDraw.Draw(lab).text((bx, by), vis, font=f, fill=(25,20,18), anchor="mm")
        base = rgba_over(base, lab)
        fr = view(base, *c, dx, dy)
    elif n == 5:
        if t < 6.26:
            c = cam([(0, (0.5, 0.31, 1.6), 0), (6.26, (0.5, 0.31, 2.0), 6.2)], t)
            fr = view(board_at(S0[2]+5), *c)
            fr = cv2.cvtColor(cv2.cvtColor(fr, cv2.COLOR_RGB2GRAY), cv2.COLOR_GRAY2RGB) if t > 0.2 else fr
            typed(layer, t, 0.3, ["THE RIVAL"], (150, 140), size=72)
            pop_word(layer, t, 3.74, "IT DIDN'T JUST COMPETE.", color=(255,255,255), size=120, y=930)
            if t >= 4.7:  # red marker X
                p = min(1, (t-4.7)/0.5); d = ImageDraw.Draw(layer); cx, cy, r = W/2, H/2+20, 330
                for (a1, a2, q) in [((cx-r, cy-r), (cx+r, cy+r), min(1, p*2)), ((cx+r, cy-r), (cx-r, cy+r), max(0, p*2-1))]:
                    if q > 0: d.line([a1, (a1[0]+(a2[0]-a1[0])*q, a1[1]+(a2[1]-a1[1])*q)], fill=(215,25,35,235), width=34)
        else:
            tt = t-6.26
            fr = view(IMG["shelf"], *cam([(0, (0.55, 0.42, 1.1), 0), (T-6.26, (0.62, 0.38, 1.45), T-6.26)], tt))
            typed(layer, t, 6.5, ["PULLED FROM THE SHELVES"], (150, 140), size=64)
            if t >= 9.3:
                p = eout((t-9.3)/0.35); cl = CLIP
                layer.alpha_composite(cl, (int(W/2-cl.width/2+40), int(H/2-cl.height/2+40+(1-p)*900)))
                stamp(layer, t, 9.95, "ACQUIRED", (W/2+330, H/2+250), size=150, rot=-12)
                dx, dy = shake(t, 9.95, 16, 0.35)
                if dx: layer = Image.fromarray(np.roll(np.asarray(layer), (int(dy), int(dx)), (0, 1)))
    elif n == 6:
        fr = view(IMG["bigboard"], *cam([(0, (0.5, 0.55, 1.0), 0), (T, (0.5, 0.5, 1.2), T)], t))
        band = np.clip(1-0.62*np.exp(-((np.arange(H)-480)/260.0)**2), 0, 1)[:, None, None] if t >= 0.2 and t < 9.3 else 1
        fr = (fr*0.75*band).astype(np.uint8)
        dx, dy = shake(t, 0.25, 22, 0.5)
        if t < 0.35: fr = np.clip(fr.astype(np.float32)*(1+1.5*(1-t/0.35)), 0, 255).astype(np.uint8)
        if t >= 0.25:
            a = int(255*ease((t-0.25)/0.25)); s = 1.0+0.06*(1-eout((t-0.25)/0.8))
            shadow_text(layer, (W/2, 395), "THE COMPANY THAT SECRETLY", font(F_SERIF, 96*s), GOLD, anchor="mm", alpha=a)
            shadow_text(layer, (W/2, 515), "OWNS YOUR GLASSES", font(F_SERIF, 124*s), GOLD, anchor="mm", alpha=a)
            # light sweep
            sw = (t-0.6)/1.0
            if 0 < sw < 1:
                m = Image.new("L", (W, H), 0); x = -300+sw*(W+600)
                ImageDraw.Draw(m).polygon([(x, 300), (x+120, 300), (x+20, 600), (x-100, 600)], fill=150)
                m = m.filter(ImageFilter.GaussianBlur(25)); la = np.asarray(layer.getchannel("A")) > 0
                sweep = Image.new("RGBA", (W, H), (255,250,230,0)); sweep.putalpha(Image.fromarray((np.asarray(m)*la).astype(np.uint8))); layer.alpha_composite(sweep)
        if t >= 1.4: typed(layer, t, 1.4, ["A GOLDSMITH PRODUCTIONS INVESTIGATION"], (W/2-560, 625), size=40, box=False, color=IVORY, cursor=False)
        if t > 8.4:  # fade title out
            arr = np.asarray(layer).copy(); arr[..., 3] = (arr[..., 3]*max(0, 1-(t-8.4)/0.8)).astype(np.uint8); layer = Image.fromarray(arr)
        if dx: layer = Image.fromarray(np.roll(np.asarray(layer), (int(dy), int(dx)), (0, 1)))
    elif n == 7:
        if t < 4.85:
            c = cam([(0, (0.5, 0.5, 1.0), 0), (1.0, (0.45, 0.5, 1.9), 1.0)], t)
            fr = view(IMG["map"], *c)
            pin_drop(layer, t, 1.05, (W*0.5, H*0.5))
            typed(layer, t, 1.4, ["MILAN, ITALY", "1935"], (W*0.5+90, H*0.5-60), size=72)
        else:
            tt = t-4.85
            fr = view(IMG["milan_market"], *cam([(0, (0.35, 0.5, 1.2), 0), (T-4.85, (0.62, 0.5, 1.2), T-4.85)], tt))
            chapter(layer, t, 5.1, "CHAPTER 1  ·  THE ORPHAN")
    elif n == 8:
        fr = view(IMG["orphan"], *cam([(0, (0.5, 0.5, 1.0), 0), (T, (0.53, 0.55, 1.3), T)], t))
        typed(layer, t, 0.45, ["RECORD: DEL VECCHIO, L.", "AGE: 7"], (1050, 150), size=50)
        stamp(layer, t, 6.25, "ORPHANAGE", (1420, 420), size=110, rot=-9)
        dx, dy = shake(t, 6.25, 14, 0.3)
        if dx: fr = np.roll(fr, (int(dy), int(dx)), (0, 1))
    return rgba_over(fr, layer)

# ---------- post ----------
VIG = None; GRAIN = None
def post(fr, g):
    out = (fr.astype(np.uint16)*VIG) >> 8
    fl = 1.0 + 0.025*math.sin(g*17.3)*math.sin(g*5.1)
    out = out.astype(np.int16) + GRAIN[int(g*FPS) % len(GRAIN)]
    out = np.clip(out*fl, 0, 255).astype(np.uint8)
    # cut punch: brief zoom-in on first frames of each scene
    for n, s in S0.items():
        if 0 < s and s <= g < s+0.2 or (n == 1 and 3.55+S0[1] <= g < 3.75):
            k = 1-(g-s if s <= g < s+0.2 else g-3.55)/0.2
            out = view(out, 0.5, 0.5, 1+0.06*k); break
    return out

def init():
    global VIG, GRAIN, CARD_F, CARD_B, CLIP
    yy, xx = np.mgrid[0:H, 0:W]; r = np.sqrt(((xx-W/2)/(W/2))**2+((yy-H/2)/(H/2))**2)
    VIG = (np.clip(1-0.42*np.clip(r-0.45, 0, 1)**1.6, 0, 1)*256).astype(np.uint16)[..., None]
    rng = np.random.default_rng(1); GRAIN = [rng.normal(0, 7, (H, W, 1)).astype(np.int16) for _ in range(6)]
    for k in ["desk", "map", "board4", "shelf", "bigboard", "milan_market", "orphan"]:
        if not os.path.exists(f"a/{k}.png"): continue  # nur Video 001 braucht alle
        IMG[k] = load_rgb(f"a/{k}.png", int(W*1.25), int(H*1.25)) if k not in ("board4",) else Image.open("a/board4.png").convert("RGBA").resize((W, H), Image.LANCZOS)
    CARD_F = card_img(True); CARD_B = card_img(False); CLIP = clipping()
    if os.path.exists("a/g_aviator.png"): init_board()

def sfx_events():
    random.seed(7); ev = []
    s = S0
    ev += [(0.05, "tick", 0.5)]
    typed_sfx(ev, s[1]+0.25, ["CASE FILE #001", "SUBJECT: UNKNOWN"])
    ev += [(s[1]+3.5, "whoosh", 0.5)]
    for t0 in (3.77, 5.90, 8.78): ev += [(s[1]+t0-0.05, "shutter", 0.55), (s[1]+t0+0.08, "slap", 0.85)]
    for t0 in (0.35, 0.95): ev += [(s[2]+t0-0.05, "shutter", 0.5), (s[2]+t0+0.08, "slap", 0.8)]
    for t0 in (1.59, 1.72, 1.85): ev += [(s[2]+t0+0.06, "slap", 0.55)]
    for t0 in (0.35, 1.59, 2.87): ev += [(s[2]+t0, "whoosh", 0.25)]
    ev += [(s[2]+4.21, "riser", 0.35)]
    ev += [(s[3]+0.25, "braam", 1.0), (s[3]+0.22, "boom", 0.7)]
    for i in range(5): ev += [(s[3]+0.30+0.13*i, "zip", 0.45)]
    ev += [(s[3]+1.68, "flip", 0.9), (s[3]+1.7, "paper", 0.4)]
    typed_sfx(ev, s[3]+5.59, ["NAME:"]); ev += [(s[3]+6.1, "zip", 0.5), (s[3]+6.62, "stamp", 0.85)]
    for t0 in [0.25, 2.37, 4.62, 7.0]:
        ev += [(s[4]+t0, "zip", 0.5), (s[4]+t0+0.4, "pin", 0.65)]
    for t0, lab in zip([0.25, 2.37, 4.62, 7.0], ["FACTORY", "THE BRANDS", "THE STORES", "THE INSURANCE"]):
        typed_sfx(ev, s[4]+t0+0.45, [lab], cps=16, gain=0.4)
    for k in range(int(PLAN[3][1])): ev += [(s[4]+k+0.5, "tick", 0.22)]
    typed_sfx(ev, s[5]+0.3, ["THE RIVAL"])
    ev += [(s[5]+3.74, "whoosh", 0.3), (s[5]+4.7, "zip", 0.7), (s[5]+4.95, "zip", 0.7), (s[5]+6.2, "whoosh", 0.5)]
    typed_sfx(ev, s[5]+6.5, ["PULLED FROM THE SHELVES"])
    ev += [(s[5]+9.3, "paper", 0.8), (s[5]+9.32, "whoosh", 0.35), (s[5]+10.0, "stamp", 1.0)]
    ev += [(s[6]-1.6, "riser", 0.55), (s[6]+0.22, "braam", 1.0), (s[6]+0.25, "boom", 0.9)]
    typed_sfx(ev, s[6]+1.4, ["A GOLDSMITH PRODUCTIONS INVESTIGATION"], gain=0.35)
    ev += [(s[7]+0.0, "whoosh", 0.4), (s[7]+1.05, "pin", 0.9), (s[7]+1.07, "boom", 0.45)]
    typed_sfx(ev, s[7]+1.4, ["MILAN, ITALY", "1935"])
    ev += [(s[7]+4.8, "whoosh", 0.5), (s[7]+5.1, "slap", 0.3)]
    ev += [(s[8]+0.0, "whoosh", 0.35)]
    typed_sfx(ev, s[8]+0.45, ["RECORD: DEL VECCHIO, L.", "AGE: 7"], gain=0.45)
    ev += [(s[8]+6.27, "stamp", 0.95)]
    return ev

def render_scene(n):
    T = dict(PLAN)[n]; init(); os.makedirs("build", exist_ok=True)
    tmp = f"build/s{n}.tmp.mp4"
    p = subprocess.Popen(["ffmpeg","-y","-loglevel","error","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-",
                          "-c:v","libx264","-preset","veryfast","-crf","19","-pix_fmt","yuv420p",tmp], stdin=subprocess.PIPE)
    N = int(round(T*FPS))
    for k in range(N):
        t = k/FPS; fr = post(frame(n, t, T), S0[n]+t)
        if n == 1 and t < 0.6: fr = (fr*(t/0.6)).astype(np.uint8)
        p.stdin.write(fr.tobytes())
    p.stdin.close()
    if p.wait() == 0: os.replace(tmp, f"build/s{n}.mp4")
    print("scene", n, "done", flush=True)

if __name__ == "__main__":
    if sys.argv[1] == "still":
        init()
        for spec in sys.argv[2:]:
            n, t = spec.split("@"); n = int(n); t = float(t)
            Image.fromarray(post(frame(n, t, dict(PLAN)[n]), S0[n]+t)).save(f"build/still_{n}_{t}.jpg", quality=88)
    elif sys.argv[1] == "scene":
        for n in sys.argv[2:]: render_scene(int(n))
    elif sys.argv[1] == "meta":
        json.dump({"plan": PLAN, "sfx": sfx_events(), "total": TOTAL}, open("build/meta.json", "w")); print(PLAN, TOTAL)
