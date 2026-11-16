"""Vorlage: Straße bei Nacht mit Ladenfront (Beispiel Luxottica: Sunglass-Hut-ähnlicher Laden, 2001 – ohne echtes Logo).
Ein Auto fährt vor und hält, eine Figur geht zur Tür, Leuchtschild flackert leicht, Straßenlaterne.
usage: python3 street_night.py <outdir> [still_frame]
Anpassen pro Video: Schildtext, Schaufenster, Autos/Figuren, Kamerafahrt, Länge.
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import dio as D

OUT = sys.argv[1]; STILL = int(sys.argv[2]) if len(sys.argv) > 2 else None
F1 = int(os.environ.get("F1", "168"))
SIGN = os.environ.get("SIGN", "SUNGLASSES")
D.reset(samples=int(os.environ.get("SAMPLES", "10")), world=(0.01, 0.015, 0.03), world_strength=1.0)

asphalt = D.nmat((0.05, 0.05, 0.055), 0.3, 3, 0.35, bump=0.1)
walk_m = D.nmat((0.25, 0.24, 0.23), 0.15, 2, 0.7)
D.box((60, 14, 0.1), (0, -4, -0.05), asphalt)                    # Straße
D.box((60, 4, 0.18), (0, 4.5, 0.09), walk_m)                      # Gehweg
D.box((60, 0.2, 0.2), (0, 2.5, 0.1), D.mat((0.4, 0.39, 0.37), 0.7))   # Bordstein
for x in range(-28, 30, 6): D.box((2.5, 0.15, 0.01), (x, -4, 0.01), D.mat((0.75, 0.72, 0.6), 0.6))   # Mittellinie
# Häuserzeile
facade = [(0.42, 0.3, 0.24), (0.3, 0.28, 0.27), (0.5, 0.42, 0.33), (0.35, 0.3, 0.26)]
for i, x in enumerate([-16, -8, 8, 16]):
    h = 9 + (i % 2)*3
    D.box((7.8, 6, h), (x, 9.5, h/2), D.nmat(facade[i], 0.12, 3, 0.9, bump=0.2))
    for fl in range(1, int(h/3)):
        for c in range(3):
            lit = (i*7+fl*3+c) % 4 == 0
            D.box((1.1, 0.1, 1.4), (x-2.4+c*2.4, 6.45, fl*3+1.2), D.mat((1, 0.66, 0.35), 0.4, emit=3.5) if lit else D.mat((0.04, 0.045, 0.06), 0.2, 0.3))
# Laden in der Mitte
D.box((8, 6, 8), (0, 9.5, 4), D.nmat((0.18, 0.17, 0.17), 0.1, 3, 0.8))
glow = D.mat((1.0, 0.82, 0.6), 0.3, emit=2.2)
D.box((5.6, 0.1, 2.6), (-0.6, 6.46, 1.6), glow)                   # Schaufenster leuchtet
D.box((1.3, 0.12, 2.4), (3.2, 6.45, 1.4), D.mat((0.08, 0.06, 0.05), 0.4))   # Tür
D.box((0.1, 0.14, 0.1), (2.8, 6.38, 1.3), D.mat((0.8, 0.7, 0.4), 0.2, 1.0))
# Leuchtschild (generisch, kein Markenlogo)
lbl = D.label_texture([SIGN], size=(1024, 200), bg=(15, 12, 10), fg=(255, 214, 140), fontsize=120)
D.textured_plane(lbl, 6.4, 1.25, (0, 6.42, 3.9), (0, 0, 0), emit=3.0)
sl = D.point((0, 5.0, 3.6), energy=60, color=(1, 0.8, 0.5), radius=0.6); D.flicker(sl, 1, F1, 60, 0.4, seed=4)
D.point((-0.6, 5.2, 1.6), energy=180, color=(1, 0.85, 0.65), radius=1.5)   # Licht aus dem Schaufenster
# Schaufenster-Inhalt: Regale mit Brillen (Silhouetten vor dem Licht)
for r in range(3):
    D.box((5.4, 0.25, 0.04), (-0.6, 6.3, 0.75+r*0.7), D.mat((0.12, 0.1, 0.09), 0.5))
    for i in range(9):
        D.glasses((-3.0+i*0.6, 6.25, 0.95+r*0.7), rot=0, size=6.0, color=(0.03, 0.03, 0.03)).rotation_euler = (math.pi/2, 0, 0)
for i in range(2): D.box((0.5, 0.5, 1.1), (-2.3+i*3.4, 6.2, 0.55), D.mat((0.1, 0.08, 0.07), 0.6))
# Straßenlaternen
for x in (-10, 10):
    D.cyl(0.08, 5.2, (x, 3.0, 2.6), D.mat((0.08, 0.08, 0.09), 0.4, 0.8), seg=10)
    D.box((0.9, 0.35, 0.2), (x-0.3, 3.0, 5.2), D.mat((0.08, 0.08, 0.09), 0.4, 0.8))
    D.box((0.6, 0.25, 0.04), (x-0.4, 3.0, 5.08), D.mat((1, 0.75, 0.4), 0.3, emit=12))
    D.spot((x-0.4, 3.0, 5.0), (x-0.4, 2.0, 0), energy=900, color=(1, 0.68, 0.35), size=95, blend=0.8, radius=0.2)
# Hydrant, Mülltonne, Bäume
D.cyl(0.18, 0.7, (-5, 3.2, 0.53), D.mat((0.5, 0.08, 0.05), 0.4), seg=12)
D.cyl(0.35, 1.0, (6.5, 3.4, 0.68), D.mat((0.15, 0.2, 0.15), 0.5, 0.4), seg=14)
for x in (-13, 13): D.tree((x, 3.4, 0.18), 5.5, seed=x+50)
# geparktes Auto + Auto, das vorfährt und hält
D.car((-9, 1.6, 0.0), rot=0, color=(0.1, 0.12, 0.16))
c = D.car((-30, -1.6, 0.0), rot=0, color=(0.55, 0.06, 0.05), lights=True)
D.drive(c, 1, 96, (-30, -1.6, 0.0), (1.8, 0.9, 0.0))
# Figur steigt aus und geht zur Ladentür
J = D.figure((2.6, 2.0, 0.18), rot=math.radians(80), shirt=(0.15, 0.14, 0.16), coat=True, hat=True, seed=8)
D.key(J["root"], 1, scale=(0.001, 0.001, 0.001)); D.key(J["root"], 104, scale=(0.001, 0.001, 0.001)); D.key(J["root"], 106, scale=(1, 1, 1))
D.sound("car_door", 100, (2.2, 1.6, 0.6), gain=0.8, ref=10)
D.walk(J, 106, F1, (2.4, 2.0, 0.18), (3.1, 5.6, 0.18))
D.sound("neon_buzz", 1, (0, 6.4, 3.9), f1=F1, loop=True, gain=0.25, ref=8)
# Passant links
J2 = D.figure((-6, 4.8, 0.18), rot=0, shirt=(0.35, 0.3, 0.25), seed=12)
D.walk(J2, 1, F1, (-7, 4.6, 0.18), (-2.5, 4.6, 0.18))

# leichter Dunst im Laternenlicht
D.beam([(-10.7, 2.9, 5.05), (-10.1, 2.9, 5.05), (-10.1, 3.1, 5.05), (-10.7, 3.1, 5.05)], (0, -0.15, -1), length=5.0, strength=0.25, color=(1, 0.7, 0.4))
D.dust((-12, 1.5, 0.3), (-8.5, 4.2, 5.0), n=140, in_beam=0, drift=(0.002, 0, -0.003))

D.camera(lens=40)
D.camera_path([(1, (-11, -21, 12.5), (0.5, 4.0, 1.6)), (F1, (-5, -17.5, 9.5), (1.6, 4.5, 1.5))])
D.render(OUT, 1, F1, still=STILL)
