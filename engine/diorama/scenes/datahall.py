"""Video 005 (Megaspeed): Rechenzentrum in Johor, 2024 – kalter Gang zwischen Server-Racks mit blinkenden LEDs,
auf dem Boden gestapelte, ungeöffnete Kartons. Ein Prüfer (von hinten) geht mit Klemmbrett den Gang entlang und
bleibt bei den Kartons stehen. Kamera gleitet langsam hinterher. Neu gebaut, realistisch, kein Tilt-Shift.
usage: python3 datahall.py <outdir> [still_frame]"""
import sys, os, math, random
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import dio as D
import assets as A

OUT = sys.argv[1]; STILL = int(sys.argv[2]) if len(sys.argv) > 2 else None
F1 = int(os.environ.get("F1", "130"))
D.reset(samples=int(os.environ.get("SAMPLES", "10")), world=(0.01, 0.012, 0.02), world_strength=1.0)
rnd = random.Random(11)
floor = A.texture("brushed_concrete", 0.6, tint=(0.35, 0.37, 0.4), rough_mul=0.5)
D.box((14, 40, 0.1), (0, 0, -0.05), floor)
D.box((14, 40, 0.1), (0, 0, 3.6), D.mat((0.05, 0.055, 0.06), 0.8))             # Decke
D.box((0.2, 40, 3.6), (-6.5, 0, 1.8), D.mat((0.12, 0.13, 0.15), 0.8))          # Seitenwände
D.box((0.2, 40, 3.6), (6.5, 0, 1.8), D.mat((0.12, 0.13, 0.15), 0.8))
D.box((14, 0.2, 3.6), (0, 18, 1.8), D.mat((0.1, 0.11, 0.13), 0.8))            # Stirnwand
rack_m = D.mat((0.035, 0.037, 0.042), 0.35, 0.6)
leds = [D.mat((0.25, 0.55, 1.0), 0.3, emit=12), D.mat((0.2, 1.0, 0.45), 0.3, emit=10), D.mat((1.0, 0.55, 0.15), 0.3, emit=8)]
# zwei Rack-Reihen links und rechts des Gangs
for side in (-1, 1):
    x = side*1.6
    for i in range(16):
        y = -12 + i*1.0
        D.box((1.1, 0.95, 2.2), (x+side*0.55, y, 1.1), rack_m)
        for r in range(9):
            if rnd.random() < 0.75:
                D.box((0.02, 0.05, 0.02), (x-side*0.005, y-0.3+rnd.random()*0.6, 0.3+r*0.2), leds[rnd.randrange(3)])
        D.box((0.01, 0.9, 0.01), (x-side*0.0, y, 2.05), D.mat((0.1, 0.4, 0.9), 0.3, emit=3))
# Kabeltrassen oben
for side in (-1, 1): D.box((0.5, 30, 0.08), (side*1.6, 3, 2.9), D.mat((0.2, 0.2, 0.22), 0.5, 0.7))
# Deckenlicht kalt, in Abständen
for y in range(-12, 17, 4):
    D.box((0.25, 1.6, 0.04), (0, y, 3.52), D.mat((0.85, 0.92, 1.0), 0.3, emit=6))
    D.point((0, y, 3.2), energy=120, color=(0.8, 0.88, 1.0), radius=0.4)
# Kartons im Gang (ungeöffnet), etwas versetzt gestapelt
box_m = D.mat((0.5, 0.36, 0.22), 0.85)
tape_m = D.mat((0.6, 0.52, 0.38), 0.4)
for k in range(14):
    bx = rnd.uniform(-0.7, 0.7); by = 2.5 + (k % 5)*0.8; bz = 0.3 + (k // 5)*0.6
    b = D.box((0.8, 0.6, 0.6), (bx*0.6, by, bz), box_m, rot=(0, 0, math.radians(rnd.uniform(-8, 8))))
    D.box((0.82, 0.08, 0.005), (bx*0.6, by, bz+0.301), tape_m)
# Prüfer mit Klemmbrett, von hinten
J = D.figure((0, -6, 0), rot=math.pi/2, shirt=(0.16, 0.17, 0.2), pants=(0.1, 0.1, 0.12), seed=21)
D.walk(J, 1, int(F1*0.75), (0, -6, 0), (0, 1.2, 0), snd="footsteps_street")
D.pose(J, int(F1*0.8), arm_r=(0, -50, 0), fore_r=(0, -70, 0), head=(0, 18, 0))
D.pose(J, F1, arm_r=(0, -55, 0), fore_r=(0, -75, 0), head=(0, 22, 8))
D.sound("neon_buzz", 1, (0, 0, 2), f1=F1, loop=True, gain=0.3, ref=10)
D.camera(lens=30)
D.camera_path([(1, (0.4, -12, 1.55), (0, 2, 1.1)), (F1, (0.25, -3.8, 1.45), (0, 3.5, 0.8))])
D.render(OUT, 1, F1, still=STILL)
