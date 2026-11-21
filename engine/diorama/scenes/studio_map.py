"""Video 004 (GTA 5): Spielestudio bei Nacht, um 2012 – Entwickler beugen sich ueber eine riesige ausgedruckte Stadtkarte
auf zusammengeschobenen Tischen, an den Waenden Monitore. Neu gebaut (keine Wiederverwendung). Realistisch, kein Tilt-Shift.
usage: python3 studio_map.py <outdir> [still_frame]"""
import sys, os, math, random
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import dio as D
import assets as A
from PIL import Image, ImageDraw, ImageFilter
OUT = sys.argv[1]; STILL = int(sys.argv[2]) if len(sys.argv) > 2 else None
F1 = int(os.environ.get("F1", "96"))
D.reset(samples=int(os.environ.get("SAMPLES", "8")))
D.world_camera_only(cam_color=(0.05, 0.06, 0.1), cam_strength=1.0, light_color=(0.02, 0.025, 0.04), light_strength=1.0)
W_, Dd, H_ = 10.0, 8.0, 3.4
D.room(W_, Dd, H_, window=dict(wall="back", u=0.3, z=0.9, w=4.0, h=2.0), wall_mat=A.texture("brick_wall_02", 0.5, tint=(0.5, 0.42, 0.38)),
       floor_mat=A.texture("wood_floor_deck", 0.6, tint=(0.55, 0.45, 0.38)))
rnd = random.Random(44)
# grosse Stadtkarte (abstrakt: Kueste, Strassenraster, Huegel) – keine echte Spielkarte
im = Image.new("RGB", (2048, 1400), (226, 214, 186)); d = ImageDraw.Draw(im)
d.polygon([(0, 1400), (0, 900), (300, 980), (700, 1150), (1100, 1250), (1500, 1300), (2048, 1260), (2048, 1400)], fill=(120, 160, 180))
for i in range(60):
    x = rnd.randint(100, 1900); d.line([(x, 0), (x+rnd.randint(-200, 200), 1200)], fill=(150, 140, 120), width=rnd.choice([2, 3, 6]))
for i in range(40):
    y = rnd.randint(50, 1150); d.line([(0, y), (2048, y+rnd.randint(-150, 150))], fill=(150, 140, 120), width=rnd.choice([2, 3, 6]))
for i in range(14): x, y, r = rnd.randint(200, 1800), rnd.randint(80, 600), rnd.randint(60, 180); d.ellipse([x-r, y-r*0.6, x+r, y+r*0.6], outline=(140, 120, 90), width=3)
for i in range(30): x, y = rnd.randint(100, 1900), rnd.randint(100, 1150); d.ellipse([x-9, y-9, x+9, y+9], fill=(200, 40, 40))
im = im.filter(ImageFilter.GaussianBlur(0.8)); im.save("/tmp/v004_citymap.png")
for x in (-1.0, 1.0):
    A.model("WoodenTable_01", (x, 0.2, 0), rot_z=0, fit_height=0.78)
D.textured_plane("/tmp/v004_citymap.png", 3.6, 2.4, (0, 0.2, 0.795), (-math.pi/2, 0, 0), emit=0.15)
# Haengelampen ueber dem Kartentisch
for x in (-0.9, 0.9):
    D.cyl(0.25, 0.14, (x, 0.2, 2.6), D.mat((0.07, 0.07, 0.07), 0.4, 0.8), r2=0.07); D.cyl(0.008, 0.8, (x, 0.2, 3.0), D.mat((0.05, 0.05, 0.05), 0.5))
    D.spot((x, 0.2, 2.5), (x, 0.2, 0), energy=170, color=(1, 0.76, 0.48), size=75, blend=0.5, radius=0.05)
# Monitorreihe an der Seitenwand (abstrakter Editor)
for k in range(4):
    p = f"/tmp/v004_ed{k}.png"; c = Image.new("RGB", (512, 300), (18, 22, 30)); cd = ImageDraw.Draw(c)
    for j in range(40):
        x0, y0 = rnd.randint(0, 460), rnd.randint(0, 260); cd.rectangle([x0, y0, x0+rnd.randint(10, 60), y0+rnd.randint(8, 40)], outline=[(90, 200, 140), (230, 170, 80), (120, 160, 240)][j % 3])
    c.save(p)
    x = -3.6+k*1.5; A.model("metal_office_desk", (x, 3.2, 0), rot_z=180, fit_height=0.76)
    D.box((0.56, 0.03, 0.34), (x, 3.45, 1.12), D.mat((0.03, 0.03, 0.035), 0.3, 0.5))
    D.textured_plane(p, 0.52, 0.30, (x, 3.432, 1.12), (0, 0, math.pi), emit=2.4)
    D.point((x, 3.1, 1.15), energy=8, color=(0.6, 0.75, 1.0), radius=0.3)
# Entwickler um den Kartentisch, einer zeigt auf die Karte, einer geht vorbei
cols = [(0.2, 0.22, 0.26), (0.38, 0.3, 0.24), (0.14, 0.14, 0.16), (0.45, 0.42, 0.4)]
spots = [((-1.6, -1.05), math.pi/2), ((0.6, -1.05), math.pi/2), ((2.25, 0.4), math.pi), ((-0.6, 1.45), -math.pi/2)]
figs = []
for i, ((x, y), r) in enumerate(spots):
    J = D.figure((x, y, 0), rot=r, shirt=cols[i], seed=40+i); figs.append(J)
    D.pose(J, 1, torso=(0, 22, 0), head=(0, 12, 0), arm_l=(0, -30, 6), arm_r=(0, -30, -6))
J = figs[1]
for f in range(1, F1, 24):
    D.pose(J, f, arm_r=(0, -75, -10), fore_r=(0, -10, 0)); D.pose(J, f+12, arm_r=(0, -68, -14), fore_r=(0, -18, 0))
D.sound("paper_flip" if True else "", 12, (0, 0.2, 0.8), gain=0.3, ref=4)
Jw = D.figure((-4.2, -2.8, 0), rot=0, shirt=(0.3, 0.32, 0.36), seed=51)
D.walk(Jw, 1, F1, (-4.2, -2.8, 0), (1.5, -2.8, 0), snd="footsteps_heels")
D.dust((-2.0, -0.8, 0.9), (2.0, 1.2, 2.5), n=160, in_beam=0)
D.camera(lens=35)
D.camera_path([(1, (0.4, -5.6, 3.6), (0.0, 0.3, 0.8)), (F1, (0.1, -4.4, 3.0), (0.0, 0.4, 0.8))])
D.render(OUT, 1, F1, still=STILL)
