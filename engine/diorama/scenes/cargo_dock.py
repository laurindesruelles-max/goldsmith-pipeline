"""Video 005 (Megaspeed): Fracht-Rampe bei Nacht (Rekonstruktion, 2024–2025) – ein weißer LKW setzt rückwärts an
das beleuchtete Rolltor einer Lagerhalle, Paletten mit eingeschweißten Server-Kartons stehen bereit, zwei Arbeiter
(von hinten/klein) gehen zur Rampe. Natriumdampf-Licht. Neu gebaut, realistisch, kein Tilt-Shift.
usage: python3 cargo_dock.py <outdir> [still_frame]"""
import sys, os, math, random
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import dio as D
import assets as A

OUT = sys.argv[1]; STILL = int(sys.argv[2]) if len(sys.argv) > 2 else None
F1 = int(os.environ.get("F1", "140"))
D.reset(samples=int(os.environ.get("SAMPLES", "10")), world=(0.02, 0.025, 0.045), world_strength=1.2)
rnd = random.Random(3)
asphalt = A.texture("asphalt_02", 0.4, tint=(0.3, 0.3, 0.32), rough_mul=0.7)
D.box((80, 60, 0.1), (0, -10, -0.05), asphalt)
# Lagerhalle mit Rampe (Rückwand bei y=+8)
wall = A.texture("chipped_concrete", 0.3, tint=(0.38, 0.38, 0.4))
D.box((40, 10, 9), (0, 13, 4.5), wall)
D.box((40, 3, 1.3), (0, 7.0, 0.65), D.mat((0.25, 0.25, 0.27), 0.7))              # Rampe
for i, x in enumerate((-9, 0, 9)):
    lit = i == 1
    D.box((4.2, 0.12, 4.0), (x, 8.0, 3.3), D.mat((1.0, 0.82, 0.55), 0.4, emit=5.0) if lit else D.mat((0.32, 0.33, 0.35), 0.5, 0.5))
    for k in range(9): D.box((4.2, 0.13, 0.03), (x, 7.98, 1.4+k*0.45), D.mat((0.2, 0.2, 0.21), 0.5))
    D.box((0.6, 0.3, 0.9), (x-2.6, 5.6, 1.1), D.mat((0.08, 0.08, 0.08), 0.8))  # Puffer
D.point((0, 6.2, 3.2), energy=900, color=(1.0, 0.8, 0.5), radius=1.5)
# Natriumdampf-Lampen an der Wand
for x in (-14, -4.5, 4.5, 14):
    D.box((0.6, 0.4, 0.25), (x, 7.8, 7.0), D.mat((1, 0.6, 0.25), 0.3, emit=25))
    D.spot((x, 7.4, 6.9), (x, 0, 0), energy=1800, color=(1, 0.6, 0.25), size=110, blend=0.7, radius=0.2)
# Paletten mit eingeschweißten Kartons auf der Rampe
wrap = D.mat((0.55, 0.45, 0.32), 0.25)
for p in range(6):
    px = -6 + p*2.4
    D.box((1.2, 1.0, 0.15), (px, 6.8, 1.38), D.mat((0.45, 0.33, 0.2), 0.8))
    D.box((1.1, 0.95, 1.1), (px, 6.8, 2.0), wrap)
# LKW setzt rückwärts an das mittlere Tor
truck = D.empty((0, -26, 0), name="truck")
_parts = [D.box((2.5, 7.0, 2.7), (0, 1.2, 2.25), D.mat((0.78, 0.78, 0.8), 0.45, 0.2)),          # Kofferaufbau (Heck zur Rampe, +y)
          D.box((2.4, 2.2, 2.2), (0, -3.6, 1.9), D.mat((0.85, 0.85, 0.87), 0.35, 0.3)),          # Fahrerhaus
          D.box((2.2, 0.05, 0.9), (0, -4.72, 2.35), D.mat((0.05, 0.07, 0.1), 0.1, 0.6)),         # Frontscheibe
          D.box((2.3, 0.1, 2.5), (0, 4.71, 2.2), D.mat((0.6, 0.6, 0.62), 0.5, 0.4)),             # Hecktuer
          D.box((0.25, 0.06, 0.15), (-0.9, 4.75, 0.95), D.mat((1, 0.1, 0.05), 0.3, emit=12)),    # Rücklichter
          D.box((0.25, 0.06, 0.15), (0.9, 4.75, 0.95), D.mat((1, 0.1, 0.05), 0.3, emit=12)),
          D.box((0.3, 0.06, 0.2), (-0.9, -4.75, 1.1), D.mat((1, 0.95, 0.8), 0.3, emit=15)),
          D.box((0.3, 0.06, 0.2), (0.9, -4.75, 1.1), D.mat((1, 0.95, 0.8), 0.3, emit=15)),
          D.box((2.5, 9.6, 0.3), (0, 0.0, 0.75), D.mat((0.08, 0.08, 0.09), 0.6, 0.5))]
for wy in (-3.6, 2.4, 3.8):
    for wx in (-1.15, 1.15): _parts.append(D.cyl(0.5, 0.35, (wx, wy, 0.5), D.mat((0.04, 0.04, 0.04), 0.8), rot=(0, math.pi/2, 0), seg=16))
for o in _parts: D.parent(o, truck)
D.drive(truck, 1, int(F1*0.85), (0, -16, 0.0), (0, 0.6, 0.0), snd=False)
D.sound("bus_engine", 1, (0, -12, 1.0), f1=int(F1*0.85), gain=0.35, ref=14)
# Arbeiter
W1 = D.figure((-5, 4.0, 0.0), rot=math.radians(-90), shirt=(0.6, 0.45, 0.15), seed=41)
D.walk(W1, 1, F1, (-6, 4.5, 0.0), (-1.6, 2.2, 0.0))
W2 = D.figure((5, 3.5, 0.0), rot=math.radians(-110), shirt=(0.2, 0.22, 0.26), seed=42)
D.walk(W2, 20, F1, (5.5, 4.2, 0.0), (2.0, 2.0, 0.0))
# Zaun + Container im Hintergrund links
for x in range(-36, -18, 3): D.cyl(0.05, 2.5, (x, 2, 1.25), D.mat((0.3, 0.3, 0.32), 0.5, 0.8), seg=6)
D.box((12, 2.6, 2.8), (-28, -4, 1.4), D.mat((0.35, 0.14, 0.1), 0.6, 0.4))
D.box((12, 2.6, 2.8), (-28, -4, 4.2), D.mat((0.12, 0.25, 0.35), 0.6, 0.4))
D.dust((-6, -2, 0.3), (6, 7, 7.0), n=120, in_beam=0, drift=(0.002, 0, -0.003))
D.camera(lens=35)
D.camera_path([(1, (-15, -20, 7.5), (0, 4, 1.8)), (F1, (-10, -15, 6.0), (0, 4.5, 1.8))])
D.render(OUT, 1, F1, still=STILL)
