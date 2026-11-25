"""Video 005 (Megaspeed): Earth-Zoom-Abstieg über einen Rechenzentrums-Campus in Johor, Malaysia (Abend).
Flaches Land mit Plantagen-Reihen, drei große Hallen mit Kühlaggregaten auf dem Dach, Zufahrtsstraße mit LKW,
Zielhalle mit hell erleuchtetem Rolltor -> Kamera sinkt bis vor das Tor. Neu gebaut, realistisch, kein Tilt-Shift.
usage: python3 aerial_johor.py <outdir> [still_frame]"""
import sys, os, math, random
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import dio as D
import assets as A

OUT = sys.argv[1]; STILL = int(sys.argv[2]) if len(sys.argv) > 2 else None
F1 = int(os.environ.get("F1", "120"))
D.reset(samples=int(os.environ.get("SAMPLES", "8")), world=(0.16, 0.2, 0.32), world_strength=0.55)
rnd = random.Random(5)
# Boden: dunkelgrünes Land + rötliche Erdwege
D.box((2400, 2400, 0.2), (0, 0, -0.1), D.nmat((0.06, 0.1, 0.05), 0.25, 3.0, 0.9))
D.box((2400, 14, 0.22), (0, -60, -0.09), D.mat((0.32, 0.17, 0.1), 0.95))
# Plantagenreihen (Palmen als kleine Bäume) rund um den Campus
for gx in range(-420, 430, 18):
    for gy in range(-420, 430, 18):
        if abs(gx) < 150 and -90 < gy < 140: continue
        if rnd.random() < 0.55: D.tree((gx+rnd.uniform(-3, 3), gy+rnd.uniform(-3, 3), 0), rnd.uniform(9, 13), seed=gx*7+gy, color=(0.08, 0.17, 0.07))
# Campus: Asphaltfläche, drei Hallen
pad = A.texture("asphalt_02", 0.02, tint=(0.3, 0.3, 0.32))
D.box((300, 230, 0.25), (0, 25, 0.0), pad)
hall_m = D.mat((0.42, 0.44, 0.47), 0.55, 0.3); roof_m = D.mat((0.4, 0.42, 0.44), 0.6, 0.4)
unit_m = D.mat((0.25, 0.27, 0.29), 0.5, 0.6)
for i, (hx, hy) in enumerate([(-80, 70), (0, 70), (80, 70)]):
    D.box((64, 90, 16), (hx, hy, 8), hall_m)
    D.box((64.5, 90.5, 0.6), (hx, hy, 16.2), roof_m)
    for ux in range(-24, 25, 8):
        for uy in range(-36, 37, 12):
            D.box((5, 8, 2.2), (hx+ux, hy+uy, 17.6), unit_m)
            D.cyl(1.6, 0.3, (hx+ux, hy+uy, 18.85), D.mat((0.1, 0.1, 0.11), 0.4, 0.6), seg=12)
    # Fensterband und Wartungslichter
    for k in range(-40, 41, 10): D.box((3, 0.1, 0.6), (hx+rnd.uniform(-20, 20), hy-45.1, 12), D.mat((0.75, 0.85, 1.0), 0.3, emit=2.0))
# Zielhalle (Mitte, Vorderseite -y): großes, warm-weiß leuchtendes Rolltor
tx, ty = 0.0, 70-45.05
door = D.box((10, 0.12, 8), (tx, ty-0.1, 4.0), D.mat((1.0, 0.9, 0.75), 0.4, emit=8.0))
D.box((11, 0.4, 0.5), (tx, ty-0.3, 8.3), D.mat((0.15, 0.15, 0.16), 0.5, 0.6))
D.point((tx, ty-3, 4), energy=4000, color=(1.0, 0.88, 0.7), radius=2.0)
# Kartons vor dem Tor (die Ware)
for k in range(9):
    D.box((1.2, 1.0, 0.9), (tx-4+(k % 3)*1.3, ty-6-(k//3)*1.1, 0.45+0.0), D.mat((0.55, 0.4, 0.25), 0.8))
# Laternen auf dem Gelände
for lx in range(-130, 131, 40):
    D.cyl(0.25, 10, (lx, -40, 5), D.mat((0.2, 0.2, 0.22), 0.4, 0.7), seg=8)
    D.sphere(0.6, (lx, -40, 10.2), D.mat((1, 0.75, 0.45), 0.3, emit=30), seg=10, ring=6)
    D.point((lx, -40, 8), energy=6000, color=(1, 0.72, 0.42), radius=1.0)
    D.spot((lx, -40, 10), (lx, -38, 0), energy=60000, color=(1, 0.72, 0.42), size=110, blend=0.8, radius=0.5)
# LKW fährt auf das Tor zu, Auto parkt
truck = D.car((-160, -60, 0.2), rot=0, color=(0.75, 0.75, 0.78), lights=True, length=9.0)
D.drive(truck, 1, int(F1*0.8), (-160, -60, 0.2), (tx-6, ty-16, 0.2))
D.car((40, -10, 0.2), rot=math.pi/2, color=(0.12, 0.14, 0.2), length=4.6)
# Wachmann vor dem Tor
J = D.figure((tx+7, ty-8, 0.25), rot=math.radians(160), shirt=(0.15, 0.18, 0.25), seed=31)
D.walk(J, 1, F1, (tx+9, ty-9, 0.25), (tx+5, ty-7, 0.25))
# tiefe Abendsonne
D.sun(rot=(math.radians(80), 0, math.radians(-50)), energy=1.6, color=(1.0, 0.5, 0.3), angle=3)
D.camera(lens=35)
D.camera_path([
    (1, (tx+5, ty-40, 1100), (tx, ty, 0), 35),
    (int(F1*0.45), (tx+40, ty-210, 220), (tx, ty+20, 4), 35),
    (int(F1*0.8), (tx+6, ty-48, 14), (tx, ty, 4.0), 40),
    (F1, (tx, ty-7.5, 4.0), (tx, ty+5, 4.0), 40),
])
D.render(OUT, 1, F1, still=STILL)
