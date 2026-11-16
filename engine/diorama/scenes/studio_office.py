"""Vorlage: Spiele-/Softwarestudio bei Nacht (Beispiel GTA 6: Rockstar North, Edinburgh – generisch, keine echten Logos/Spielbilder).
Schreibtischreihen mit Monitoren (abstrakter Code/Leveleditor), Entwickler an den Tischen, einer geht mit Kaffee vorbei,
großes Fenster mit nächtlicher Stadt, Lampenkegel mit Staub. usage: python3 studio_office.py <outdir> [still_frame]
"""
import sys, os, math, random
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import dio as D
import assets as A

OUT = sys.argv[1]; STILL = int(sys.argv[2]) if len(sys.argv) > 2 else None
F1 = int(os.environ.get("F1", "168"))
D.reset(samples=int(os.environ.get("SAMPLES", "8")))
D.world_camera_only(cam_color=(0.05, 0.07, 0.12), cam_strength=1.0, light_color=(0.02, 0.025, 0.04), light_strength=1.0)
W_, Dd, H_ = 9.0, 7.0, 3.4
win = dict(wall="back", u=0.5, z=0.8, w=5.5, h=2.2)
D.room(W_, Dd, H_, window=win, wall_mat=A.texture("plastered_wall", 0.5, tint=(0.45, 0.45, 0.48)),
       floor_mat=A.texture("concrete_floor_02", 0.4, tint=(0.55, 0.55, 0.58)))
# Nächtliche Stadt hinter dem Fenster (leuchtende Fassaden mit Fensterrastern)
from PIL import Image, ImageDraw
im = Image.new("RGB", (2048, 800), (8, 12, 22)); d = ImageDraw.Draw(im); rnd = random.Random(3)
for b in range(26):
    x0 = rnd.randint(0, 1950); w = rnd.randint(70, 200); h = rnd.randint(250, 760); y0 = 800-h
    d.rectangle([x0, y0, x0+w, 800], fill=(14, 16, 24))
    for yy in range(y0+12, 790, 22):
        for xx in range(x0+8, x0+w-10, 16):
            if rnd.random() < 0.35: d.rectangle([xx, yy, xx+8, yy+11], fill=(255, rnd.randint(170, 215), rnd.randint(90, 140)))
im.save("/tmp/citynight.png")
sky = D.textured_plane("/tmp/citynight.png", 16, 6.25, (0.5, Dd/2+5, 2.6), (0, 0, 0), emit=1.6); D.no_shadow(sky)
# Schreibtischreihen mit Monitoren
code = []
for k in range(4):
    lines = ["".join(rnd.choice("abcdefghijklmnopqrstuvwxyz_(){}=;. ") for _ in range(rnd.randint(14, 30))) for _ in range(9)]
    p = f"/tmp/code{k}.png"; c = Image.new("RGB", (512, 300), (14, 18, 26)); cd = ImageDraw.Draw(c)
    for i, ln in enumerate(lines): cd.text((14, 10+i*31), ln, fill=[(120, 220, 160), (200, 200, 215), (240, 180, 90), (130, 170, 255)][(i+k) % 4])
    c.save(p); code.append(p)
desks = []
for row, y in enumerate((-1.2, 0.9)):
    for col, x in enumerate((-2.6, -0.4, 1.8)):
        A.model("metal_office_desk", (x, y, 0), rot_z=0, fit_height=0.76)
        for m, dx in enumerate((-0.35, 0.35)):
            D.box((0.06, 0.06, 0.25), (x+dx, y+0.25, 0.88), D.mat((0.05, 0.05, 0.06), 0.4, 0.6))
            D.box((0.56, 0.03, 0.34), (x+dx, y+0.25, 1.12), D.mat((0.03, 0.03, 0.035), 0.3, 0.5))
            D.textured_plane(code[(row*3+col+m) % 4], 0.52, 0.30, (x+dx, y+0.232, 1.12), (0, 0, 0), emit=2.2)
        D.point((x, y-0.1, 1.15), energy=8, color=(0.6, 0.75, 1.0), radius=0.3)          # Bildschirmlicht
        desks.append((x, y))
# Hängelampen mit warmem Kegel
for x in (-2.6, -0.4, 1.8):
    D.cyl(0.22, 0.12, (x, -0.15, 2.7), D.mat((0.08, 0.08, 0.08), 0.4, 0.8), r2=0.06); D.cyl(0.008, 0.7, (x, -0.15, 3.05), D.mat((0.05, 0.05, 0.05), 0.5))
    D.spot((x, -0.15, 2.62), (x, -0.15, 0), energy=120, color=(1, 0.75, 0.45), size=70, blend=0.5, radius=0.05)
    D.beam([(x-0.18, -0.33, 2.62), (x+0.18, -0.33, 2.62), (x+0.18, 0.03, 2.62), (x-0.18, 0.03, 2.62)], (0, 0, -1), length=2.4, strength=0.22, color=(1, 0.78, 0.5))
D.dust((-3.2, -1.0, 0.3), (2.6, 0.7, 2.6), n=260, in_beam=0)
# Requisiten
A.model("steel_frame_shelves_01", (-W_/2+0.5, 2.2, 0), rot_z=90, fit_height=2.0)
A.model("potted_plant_01", (3.8, 2.6, 0), fit_height=1.3)
A.model("cardboard_box_01", (3.6, -1.8, 0), rot_z=25)
# Entwickler an den Tischen (gedeckte Kleidung), Tipp-Bewegung
cols = [(0.18, 0.2, 0.24), (0.35, 0.3, 0.26), (0.12, 0.12, 0.13), (0.4, 0.42, 0.45)]
for i, (x, y) in enumerate([desks[0], desks[2], desks[4]]):
    J = D.figure((x+0.05, y-0.55, 0), rot=math.pi/2, shirt=cols[i], seed=20+i)
    D.pose(J, 1, torso=(0, 14, 0), head=(0, 8, 0), arm_l=(0, -55, 8), fore_l=(0, -45, 0), arm_r=(0, -55, -8), fore_r=(0, -45, 0))
    for f in range(1+i*3, F1, 10):
        D.pose(J, f, fore_l=(0, -45, 0), fore_r=(0, -40, 0)); D.pose(J, f+5, fore_l=(0, -40, 0), fore_r=(0, -46, 0))
    D.sound("keyboard_typing" if os.path.exists(os.path.join(os.path.dirname(__file__), "../../../assets/sfx/keyboard_typing.wav")) else "marker_write", 1+i*20, (x, y, 0.8), gain=0.25, ref=4)
Jw = D.figure((-4.0, -2.5, 0), rot=0, shirt=(0.5, 0.18, 0.12), seed=33)
D.walk(Jw, 1, F1, (-4.0, -2.4, 0), (3.2, -2.4, 0), snd="footsteps_heels")
D.sound("amb_lab", 1, (0, 0, 1.5), f1=F1, loop=True, gain=0.25, ref=8)
D.camera(lens=38)
D.camera_path([(1, (6.2, -7.4, 5.6), (-0.4, 0.2, 0.8)), (F1, (4.4, -5.4, 4.2), (-0.6, 0.0, 0.9))])
D.render(OUT, 1, F1, still=STILL)
