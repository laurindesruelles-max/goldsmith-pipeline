"""Vorlage: Werkstatt-Innenraum (Beispiel Luxottica: Agordo 1961, Del Vecchio an der Werkbank).
usage: python3 workshop.py <outdir> [still_frame]
Anpassen pro Video: Kalender-/Schildtext, Figuren, Requisiten, Kamerafahrt, Länge.
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import dio as D

OUT = sys.argv[1]; STILL = int(sys.argv[2]) if len(sys.argv) > 2 else None
F1 = int(os.environ.get("F1", "240"))
D.reset(samples=int(os.environ.get("SAMPLES", "10")))
D.world_camera_only(cam_color=(1.0, 0.78, 0.5), cam_strength=1.6, light_color=(0.03, 0.035, 0.05), light_strength=1.0)

W_, Dd, H_ = 6.0, 5.0, 3.2
win = dict(wall="back", u=-0.5, z=1.05, w=1.5, h=1.45)
R = D.room(W_, Dd, H_, wall=(0.5, 0.43, 0.35), floor=(0.2, 0.13, 0.08), window=win)

# Bergkulisse hinter dem Fenster (leuchtende Fläche)
sky = D.box((14, 0.1, 6), (-0.9, Dd/2+4, 2.5), D.mat((1.0, 0.72, 0.42), 1.0, emit=2.2)); D.no_shadow(sky)
for i, (x, h) in enumerate([(-5, 3.5), (-2.5, 4.6), (0.3, 3.8), (2.8, 5.0), (5, 3.2)]):
    D.no_shadow(D.cyl(2.6, h, (x, Dd/2+3.8, h/2-0.2), D.mat((0.55, 0.42, 0.35), 1.0, emit=0.6, emit_color=(0.9, 0.6, 0.4)), seg=5, r2=0.05))

# Sonne schräg durchs Fenster (Nachmittag)
sun_dir = (-0.45, -1.0, -0.5)
s = D.sun(energy=9.0, color=(1.0, 0.78, 0.52), angle=1.0); s.location = (0, 10, 6)
from mathutils import Vector
s.rotation_euler = Vector(sun_dir).to_track_quat("-Z", "Y").to_euler()
D.area((2.5, -4, 3.5), (-1, 0.5, 0.8), energy=140, color=(0.55, 0.65, 0.9), size=3)
D.point((0.5, 0.0, 2.9), energy=25, color=(1, 0.7, 0.45), radius=0.2)   # warme Raumaufhellung   # kühles Fülllicht

# Werkbank an der linken Wand
wood = D.nmat((0.32, 0.2, 0.11), 0.3, 4, 0.55, stripes=True); dark = D.mat((0.08, 0.08, 0.085), 0.4, 0.8)
bx, by = -W_/2+0.45, 0.2
D.box((0.8, 2.6, 0.08), (bx, by, 0.92), wood, bevel=0.01)
for yy in (by-1.2, by+1.2):
    for xx in (bx-0.33, bx+0.33): D.box((0.07, 0.07, 0.9), (xx, yy, 0.45), wood)
D.box((0.75, 2.5, 0.04), (bx, by, 0.3), wood)
D.box((0.18, 0.14, 0.14), (bx+0.25, by+0.6, 1.03), dark, bevel=0.01)   # Schraubstock
D.box((0.24, 0.05, 0.03), (bx+0.25, by+0.6, 1.11), dark)
D.lamp = D.desk_lamp((bx-0.15, by-0.7, 0.96), (bx+0.2, by-0.1, 0.96), energy=35)
# Brillengestelle + Teile auf der Werkbank
tray = D.box((0.36, 0.26, 0.025), (bx+0.12, by-0.15, 0.975), D.mat((0.55, 0.5, 0.42), 0.7))
for i in range(6):
    D.glasses((bx+0.04+(i % 2)*0.16, by-0.24+(i//2)*0.09, 0.99), rot=math.radians(90+(i*7) % 15), metal=(i % 3 == 0), color=(0.75, 0.6, 0.3) if i % 3 == 0 else (0.06, 0.04, 0.03))
for i in range(5):
    D.cyl(0.006, 0.18, (bx+0.3, by+0.15+i*0.05, 0.97), dark, rot=(0, math.pi/2, 0), seg=8)   # Feilen
# Regal an der Rückwand rechts mit Kisten
for k in range(3):
    D.box((1.6, 0.35, 0.04), (1.6, Dd/2-0.25, 0.9+k*0.6), wood)
    for j in range(4):
        D.box((0.3, 0.25, 0.2), (1.0+j*0.4, Dd/2-0.27, 1.02+k*0.6), D.mat([(0.45, 0.36, 0.25), (0.38, 0.3, 0.2), (0.5, 0.42, 0.3)][(j+k) % 3], 0.85))
# Kalender + Schild an der linken Wand
cal = D.label_texture(["MAGGIO", "1961"], size=(300, 380), fontsize=62)
D.textured_plane(cal, 0.32, 0.42, (-W_/2+0.07, by+0.9, 1.75), (0, 0, math.radians(90)))
sign = D.label_texture(["OCCHIALERIA"], size=(640, 160), bg=(60, 45, 30), fg=(225, 200, 150), fontsize=64)
D.textured_plane(sign, 1.1, 0.27, (-W_/2+0.07, by-0.4, 2.3), (0, 0, math.radians(90)))
# Hocker, Kiste am Boden
D.cyl(0.18, 0.05, (bx+1.5, by+1.1, 0.6), wood); D.cyl(0.02, 0.6, (bx+1.5, by+1.1, 0.3), dark)
D.box((0.5, 0.4, 0.35), (1.8, -0.8, 0.175), D.mat((0.4, 0.3, 0.2), 0.85))


# mehr Leben: Wandregal mit Gläsern über der Werkbank, Uhr, Mantel am Haken, Papierstapel, Radio
D.box((0.25, 1.4, 0.03), (-W_/2+0.18, by-0.2, 1.65), wood)
for i in range(6):
    D.cyl(0.045, 0.12, (-W_/2+0.18, by-0.8+i*0.24, 1.73), D.mat([(0.35, 0.5, 0.4), (0.6, 0.45, 0.25), (0.3, 0.3, 0.35)][i % 3], 0.15, alpha=1.0), seg=12)
D.cyl(0.16, 0.03, (-W_/2+0.08, by+1.6, 2.2), D.mat((0.9, 0.88, 0.8), 0.6), rot=(0, math.pi/2, 0), seg=24)   # Uhr
D.torus(0.16, 0.012, (-W_/2+0.1, by+1.6, 2.2), D.mat((0.1, 0.08, 0.06), 0.4), rot=(0, math.pi/2, 0))
D.box((0.06, 0.32, 0.75), (-W_/2+0.1, -1.9, 1.55), D.nmat((0.22, 0.2, 0.17), 0.2, 8))   # Mantel
D.sphere(0.03, (-W_/2+0.08, -1.9, 1.95), D.mat((0.3, 0.25, 0.1), 0.3, 1.0))
for i in range(4): D.box((0.21, 0.29, 0.006), (bx+0.05, by+0.95, 0.965+i*0.007), D.mat((0.9, 0.87, 0.78), 0.8), rot=(0, 0, math.radians(i*6)))
D.box((0.28, 0.14, 0.17), (bx-0.1, by+1.05, 1.05), D.nmat((0.35, 0.22, 0.12), 0.2, 6, 0.4, stripes=True), bevel=0.015)   # Radio
D.box((0.2, 0.005, 0.1), (bx-0.1+0.02, by+1.05-0.071, 1.06), D.mat((0.85, 0.75, 0.5), 0.5, emit=0.8, emit_color=(1, 0.75, 0.4)))

# Figur: junger Handwerker an der Werkbank (Blick zur Wand, -x)
J = D.figure((bx+0.72, by-0.05, 0), rot=math.pi, shirt=(0.62, 0.6, 0.55), pants=(0.12, 0.12, 0.14), apron=(0.18, 0.13, 0.09), seed=3)
D.pose(J, 1, torso=(0, 12, 0), head=(0, 18, 0), arm_l=(0, -45, 8), fore_l=(0, -55, 0), arm_r=(0, -40, -6), fore_r=(0, -60, 0))
for f in range(1, F1+1, 16):   # Feilen: rechter Arm vor und zurück
    D.pose(J, f, arm_r=(0, -40, -6), fore_r=(0, -60, 0))
    D.pose(J, f+8, arm_r=(0, -58, -6), fore_r=(0, -38, 0))
D.pose(J, 120, head=(0, 18, 0)); D.pose(J, 150, head=(0, 10, 12)); D.pose(J, 200, head=(0, 18, 0))

# Lichtstrahl durchs Fenster + Staub darin
y0 = Dd/2; u, z0, ww, wh = win["u"], win["z"], win["w"], win["h"]
corners = [(u-ww/2, y0, z0), (u+ww/2, y0, z0), (u+ww/2, y0, z0+wh), (u-ww/2, y0, z0+wh)]
D.beam(corners, sun_dir, length=3.6, strength=0.55)
D.dust((u-2.0, -0.8, 0.5), (u+0.9, y0-0.1, 2.6), n=340, in_beam=0)

# Kamera: langsam von halbtotal auf die Werkbank (leichter Bogen)
D.camera(lens=45)
D.camera_path([(1, (3.9, -4.6, 4.3), (-0.9, 0.5, 0.7), 50), (F1, (2.6, -3.0, 3.1), (-1.5, 0.2, 0.95), 50)])
D.render(OUT, 1, F1, still=STILL)
