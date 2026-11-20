"""Ton fuer die Goldsmith-Stilprobe: nur Laurins abgenommene Goldsmith-Sounds + Goldsmith-Musik."""
import random, sys
sys.path.insert(0, "/home/claude/stilproben")
from mixer import mix
S = "/home/claude/gs_sfx/"; M = "/home/claude/repos/goldsmith-pipeline/assets/music/"
f = lambda n: S + n + ".wav"
random.seed(3); ev = []
def typed(t0, text, cps=14, g=0.45):
    for k, ch in enumerate(text):
        if ch != " ": ev.append((t0 + k / cps, f(f"key{random.randint(0, 6)}"), g))
# 1) Schreibtisch: Akte wird zugeschoben, Ort tippen
ev += [(0.45, f("paper_slide"), 0.85), (0.5, f("whoosh"), 0.18), (1.35, f("paper"), 0.45)]
typed(2.0, "PARIS, 2017")
# 2) Wand waechst: Polaroid = Ausloeser + Aufprall + Nadel (Goldsmith-Muster), Faden = zip
ev += [(4.42, f("whoosh"), 0.3)]
for t0 in (4.9, 6.6, 8.3, 10.0):
    ev += [(t0 - 0.05, f("shutter"), 0.5), (t0 + 0.08, f("slap"), 0.75), (t0 + 0.22, f("pin"), 0.6)]
for t0 in (5.9, 7.6, 9.3, 11.2):
    ev += [(t0, f("zip"), 0.42)]
ev += [(12.0, f("stamp"), 1.3), (12.02, f("braam"), 0.9), (12.02, f("boom"), 0.5)]
for k in range(5, 18): ev += [(k + 0.5, f("tick"), 0.2)]
# Rueckzoom + Lampe
ev += [(13.25, f("whoosh"), 0.32), (15.2, f("lever"), 0.25), (18.2, f("sub_drop"), 0.25)]
music = (M + "crime_pulse.mp3", 0.24, 4.4, 1.5, 1.2, [(11.75, -18, 0.3), (12.8, 3, 1.2)])
print(mix("/home/claude/stilproben/stilprobe_goldsmith.mp4", "/home/claude/stilproben/ton_goldsmith.mp4", ev, 19.0, music))
