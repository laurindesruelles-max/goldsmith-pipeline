"""Animierte Daten-Grafiken (Laurin 16.11.: mehr Bewegung + Diagramme). Kostenlos, alles prozedural.
Kinds (spec.json, Vollbild, Dauer default 5.5 s oder "dur"):
  ["bars", anchor, {"title": "...", "items": [["PS5", 703, "$703M"], ["XBOX", 239, "$239M"]], "hl": 0, "source": "..."}]
  ["breakdown", anchor, {"total": 80, "parts": [["PLATFORM", 24, "30%"], ["TAKE-TWO", 56, "70%"]], "hl": 0|1|None, "note": "..."}]
  ["timeline", anchor, {"title": "...", "steps": [["2025", "PLANNED", "x"], ["MAY 2026", "DELAYED", "x"], ["NOV 19, 2026", "LAUNCH", "ok"]]}]
  ["flow", anchor, {"nodes": ["YOU", "CONSOLE STORE", "SONY / MICROSOFT", "TAKE-TWO"], "labels": ["$80", "30%", "70%"]}]
Hintergrund = abgedunkeltes, unscharfes Szenenbild, das langsam driftet (nie Standbild).
"""
import math, numpy as np, cv2
from PIL import Image, ImageDraw, ImageFilter
from effects import W, H, f, ANTON, TYPE, INTER, GOLD, IVORY, RED, ease, eout, empty, view, source_line

TEAL = (70, 200, 220); GREEN = (60, 190, 110); GREY = (150, 150, 150)
_BG = {}

def bg(ctx, t, T, dark=0.28):
    b = ctx.get("bg")
    if b is None: return np.full((H, W, 3), 16, np.uint8)
    k = ctx.get("n", id(b))
    if k not in _BG: _BG.clear(); _BG[k] = cv2.GaussianBlur(b, (0, 0), 18)
    fr = view(_BG[k], 0.5+0.04*math.sin(t*0.4), 0.5, 1.12+0.05*t/max(T, 1))
    return (fr*dark).astype(np.uint8)

def _title(d, txt, t):
    if not txt: return
    a = int(255*ease(t/0.4)); d.text((W/2, 120), txt, font=f(TYPE, 48), fill=IVORY+(a,), anchor="mm")
    w = f(TYPE, 48).getlength(txt); d.line([(W/2-w/2, 160), (W/2-w/2+w*eout((t-0.2)/0.6), 160)], fill=RED+(a,), width=4)

def _fin(fr, layer, p, t):
    if p.get("source"): source_line(layer, "SOURCE: "+p["source"], min(1.0, t/0.5))
    return fr, layer

# ---------- bars: horizontale Balken, wachsen nacheinander, Werte zählen hoch ----------
def bars(t, T, p, ctx):
    fr = bg(ctx, t, T); layer = empty(); d = ImageDraw.Draw(layer); _title(d, p.get("title", ""), t)
    items = p["items"]; n = len(items); vmax = max(v for _, v, *_ in items)
    top = 300 if n <= 3 else 250; gap = min(190, 560//n); bh = int(gap*0.55); x0, x1 = 560, 1440
    for i, it in enumerate(items):
        lab, v, txt = it[0], it[1], (it[2] if len(it) > 2 else str(v))
        t0 = 0.5+0.45*i; pr = eout((t-t0)/1.1)
        if t < t0-0.2: continue
        a = int(255*ease((t-t0+0.2)/0.3)); y = top+i*gap
        hl = p.get("hl") == i; col = GOLD if hl else (IVORY if p.get("hl") is None else (120, 115, 105))
        if it[3:] and it[3] == "red": col = RED
        d.text((x0-30, y+bh/2), lab, font=f(ANTON, 64 if n <= 4 else 52), fill=IVORY+(a,), anchor="rm")
        wbar = (x1-x0)*v/vmax*pr
        d.rectangle([x0, y, x0+wbar, y+bh], fill=col+(min(a, 235),))
        d.rectangle([x0, y+bh-6, x0+wbar, y+bh], fill=(0, 0, 0, 60))
        if pr > 0.05:
            d.text((x0+wbar+24, y+bh/2), txt, font=f(ANTON, 70 if n <= 4 else 56), fill=col+(a,), anchor="lm")
    if p.get("note") and t > 0.6+0.45*n+0.6:
        a = int(255*ease((t-(0.6+0.45*n+0.6))/0.4)); d.text((W/2, H-170), p["note"], font=f(TYPE, 40), fill=IVORY+(a,), anchor="mm")
    return _fin(fr, layer, p, t)

# ---------- breakdown: ein 80-$-Balken teilt sich auf ----------
def breakdown(t, T, p, ctx):
    fr = bg(ctx, t, T); layer = empty(); d = ImageDraw.Draw(layer)
    tot = p.get("total", 80); parts = p["parts"]; x0, x1, y0, y1 = 260, 1660, 430, 610
    d.text((W/2, 250), f"${tot}", font=f(ANTON, 170), fill=IVORY+(int(255*ease(t/0.4)),), anchor="mm")
    grow = eout((t-0.3)/0.8); d.rectangle([x0, y0, x0+(x1-x0)*grow, y1], fill=(60, 56, 50, 255))
    sp = eout((t-1.3)/0.7); cols = [TEAL, GOLD, GREEN, RED]; x = x0; gapw = 24*sp
    for i, (lab, v, pct) in enumerate(parts):
        w = (x1-x0-gapw*(len(parts)-1))*v/tot
        hl = p.get("hl"); dim = hl is not None and hl != i
        col = tuple(int(c*(0.35 if dim else 1)) for c in cols[i % 4])
        if sp > 0:
            lift = -18*eout((t-2.2)/0.4) if hl == i else 0
            d.rectangle([x, y0+lift, x+w*grow, y1+lift], fill=col+(int(255*sp),))
            a = int(255*ease((t-1.6-0.3*i)/0.4))
            if a > 0:
                d.text((x+w/2, y0+lift+(y1-y0)/2), f"${v}", font=f(ANTON, 96), fill=(20, 18, 16, a), anchor="mm")
                d.text((x+w/2, y1+70), lab, font=f(ANTON, 58), fill=(col if not dim else (120, 115, 105))+(a,), anchor="mm")
                d.text((x+w/2, y1+130), pct, font=f(TYPE, 40), fill=IVORY+(int(a*(0.5 if dim else 1)),), anchor="mm")
        x += w+gapw
    if p.get("note") and t > 2.6:
        a = int(255*ease((t-2.6)/0.4)); d.text((W/2, H-150), p["note"], font=f(TYPE, 38), fill=IVORY+(a,), anchor="mm")
    return _fin(fr, layer, p, t)

# ---------- timeline: Linie läuft, Termine werden durchgestrichen ----------
def timeline(t, T, p, ctx):
    fr = bg(ctx, t, T); layer = empty(); d = ImageDraw.Draw(layer); _title(d, p.get("title", ""), t)
    st = p["steps"]; n = len(st); xs = [300+i*(1320/(n-1)) for i in range(n)]; y = 560
    ln = eout((t-0.3)/(0.9*n)); d.line([(xs[0], y), (xs[0]+(xs[-1]-xs[0])*ln, y)], fill=IVORY+(220,), width=6)
    for i, (date, lab, kind) in enumerate(st):
        t0 = 0.4+0.9*i
        if t < t0: continue
        a = int(255*ease((t-t0)/0.3)); ok = kind == "ok"; col = GOLD if ok else IVORY
        r = 22+10*(1-eout((t-t0)/0.3)); d.ellipse([xs[i]-r, y-r, xs[i]+r, y+r], fill=col+(a,))
        d.text((xs[i], y-90), date, font=f(ANTON, 76 if ok else 64), fill=col+(a,), anchor="mm")
        d.text((xs[i], y+80), lab, font=f(TYPE, 40), fill=IVORY+(a,), anchor="mm")
        if not ok:
            pr = eout((t-t0-0.45)/0.3); w = f(ANTON, 64).getlength(date)/2+16
            if pr > 0: d.line([(xs[i]-w, y-90), (xs[i]-w+2*w*pr, y-90)], fill=RED+(255,), width=10)
        else:
            s = 1+0.25*(1-eout((t-t0-0.3)/0.3))
            if t > t0+0.3: d.text((xs[i], y+160), p.get("final", "LAUNCH"), font=f(ANTON, int(64*s)), fill=RED+(255,), anchor="mm")
    return _fin(fr, layer, p, t)

# ---------- flow: Geldfluss Käufer -> Store -> Plattform / Publisher, Münzen wandern ----------
def flow(t, T, p, ctx):
    fr = bg(ctx, t, T); layer = empty(); d = ImageDraw.Draw(layer)
    nodes = p["nodes"]; labs = p.get("labels", ["", "", ""])
    P = [(330, 540), (960, 540), (1590, 330), (1590, 760)]
    def box(i, a):
        x, y = P[i]; txt = nodes[i]; w = max(260, f(ANTON, 54).getlength(txt)+70)
        d.rounded_rectangle([x-w/2, y-70, x+w/2, y+70], 18, fill=(28, 26, 24, a), outline=(GOLD if i == 1 else IVORY)+(a,), width=4)
        d.text((x, y), txt, font=f(ANTON, 54), fill=IVORY+(a,), anchor="mm")
    edges = [(0, 1, 0.9), (1, 2, 2.0), (1, 3, 2.6)]
    for i, t0 in enumerate([0.2, 0.7, 1.7, 2.3]):
        if t > t0: box(i, int(255*ease((t-t0)/0.3)))
    for k, (a_, b_, t0) in enumerate(edges):
        if t < t0: continue
        (xa, ya), (xb, yb) = P[a_], P[b_]; xa += 160 if a_ == 0 else 150; xb -= 170
        pr = eout((t-t0)/0.5); xe, ye = xa+(xb-xa)*pr, ya+(yb-ya)*pr
        d.line([(xa, ya), (xe, ye)], fill=GOLD+(230,), width=6)
        if labs[k] and pr > 0.6:
            d.text(((xa+xb)/2, (ya+yb)/2-50), labs[k], font=f(ANTON, 60), fill=GOLD+(255,), anchor="mm", stroke_width=4, stroke_fill=(0, 0, 0, 255))
        if pr >= 1:   # wandernde Münzen
            for j in range(4):
                u = ((t-t0)*0.8+j/4) % 1; cx, cy = xa+(xb-xa)*u, ya+(yb-ya)*u
                d.ellipse([cx-13, cy-13, cx+13, cy+13], fill=(240, 200, 90, 255), outline=(150, 110, 30, 255), width=3)
    return _fin(fr, layer, p, t)

RENDER = {"bars": bars, "breakdown": breakdown, "timeline": timeline, "flow": flow}
DUR = {"bars": 5.5, "breakdown": 5.5, "timeline": 5.0, "flow": 5.5}
SOUNDS = {"bars": [(0.5, "zip", 0.35), (0.95, "zip", 0.3), (1.4, "zip", 0.3)],
          "breakdown": [(0.3, "zip", 0.4), (1.3, "slap", 0.5)],
          "timeline": [(0.4, "pin", 0.5), (1.3, "pin", 0.5), (2.2, "pin", 0.5)],
          "flow": [(0.9, "zip", 0.4), (2.0, "coins", 0.4), (2.6, "zip", 0.35)]}
