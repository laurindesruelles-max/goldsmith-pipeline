"""Video 004 (GTA 5): Hobby-Programmierer nachts am Schreibtisch im Zimmer (2021), zwei Monitore mit Code bzw. Ladebalken,
Schreibtischlampe, Fenster mit Nachtstadt, Energydosen. Figur tippt, lehnt sich dann zurueck. Neu gebaut. Realistisch, kein Tilt-Shift.
usage: python3 coder_room.py <outdir> [still_frame]"""
import sys, os, math, random
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import dio as D
import assets as A
from PIL import Image, ImageDraw
OUT = sys.argv[1]; STILL = int(sys.argv[2]) if len(sys.argv) > 2 else None
F1 = int(os.environ.get("F1", "110"))
D.reset(samples=int(os.environ.get("SAMPLES", "8")))
D.world_camera_only(cam_color=(0.04, 0.05, 0.09), cam_strength=1.0, light_color=(0.02, 0.02, 0.035), light_strength=1.0)
W_, Dd, H_ = 5.0, 4.5, 2.8
D.room(W_, Dd, H_, window=dict(wall="back", u=0.72, z=1.0, w=1.6, h=1.3), wall_mat=A.texture("plastered_wall", 0.5, tint=(0.42, 0.44, 0.5)),
       floor_mat=A.texture("wood_floor_deck", 0.7, tint=(0.5, 0.4, 0.33)))
rnd = random.Random(7)
im = Image.new("RGB", (1024, 600), (10, 14, 26)); d = ImageDraw.Draw(im)
for b in range(14):
    x0 = rnd.randint(0, 950); w = rnd.randint(60, 160); h = rnd.randint(200, 560)
    d.rectangle([x0, 600-h, x0+w, 600], fill=(16, 18, 26))
    for yy in range(600-h+10, 590, 20):
        for xx in range(x0+6, x0+w-8, 14):
            if rnd.random() < 0.3: d.rectangle([xx, yy, xx+7, yy+10], fill=(255, 200, 120))
im.save("/tmp/v004_night.png")
sky = D.textured_plane("/tmp/v004_night.png", 6, 3.5, (W_*0.22, Dd/2+3, 1.6), (0, 0, 0), emit=1.4); D.no_shadow(sky)
A.model("WoodenTable_01", (-0.6, 1.2, 0), rot_z=0, fit_height=0.76)
# Monitor 1: Code, Monitor 2: Ladebalken (wird im Clip gefuellt -> zwei Texturzustaende ueber Sichtbarkeit)
code = Image.new("RGB", (640, 380), (14, 16, 22)); cd = ImageDraw.Draw(code)
for i in range(12):
    ln = "".join(rnd.choice("abcdefghijklmnopqrstuvwxyz_(){}=;.<> ") for _ in range(rnd.randint(16, 44)))
    cd.text((16, 12+i*30), ln, fill=[(120, 220, 160), (210, 210, 220), (240, 180, 90), (130, 170, 255)][i % 4])
cd.rectangle([10, 12+6*30-4, 630, 12+6*30+24], outline=(230, 60, 60), width=3)
code.save("/tmp/v004_code.png")
for x, p in ((-1.0, "/tmp/v004_code.png"), (-0.2, None)):
    D.box((0.62, 0.04, 0.38), (x, 1.55, 1.08), D.mat((0.03, 0.03, 0.035), 0.3, 0.5)); D.box((0.06, 0.06, 0.22), (x, 1.58, 0.86), D.mat((0.05, 0.05, 0.06), 0.4, 0.6))
    if p: D.textured_plane(p, 0.58, 0.34, (x, 1.528, 1.08), (0, 0, 0), emit=2.4)
# Ladebalken: dunkles Feld + wachsender gruener Balken
D.textured_plane("/tmp/v004_code.png", 0.001, 0.001, (0, 0, -5), (0, 0, 0))
bgp = Image.new("RGB", (64, 64), (20, 24, 32)); bgp.save("/tmp/v004_bg.png")
D.textured_plane("/tmp/v004_bg.png", 0.58, 0.34, (-0.2, 1.528, 1.08), (0, 0, 0), emit=1.5)
bar = D.box((0.5, 0.005, 0.05), (-0.2, 1.522, 1.05), D.mat((0.3, 0.95, 0.45), 0.3, emit=6.0))
D.key(bar, 1, loc=(-0.2-0.25+0.01, 1.522, 1.05), scale=(0.02, 1, 1)); D.key(bar, int(F1*0.85), loc=(-0.2, 1.522, 1.05), scale=(1, 1, 1))
D.point((-0.6, 1.2, 1.15), energy=10, color=(0.55, 0.7, 1.0), radius=0.3)
# Requisiten: Tastatur, Dosen, Lampe, Regal
D.box((0.45, 0.15, 0.025), (-0.6, 1.15, 0.775), D.mat((0.06, 0.06, 0.07), 0.5))
for i, x in enumerate((0.15, 0.27, 0.05)): D.cyl(0.033, 0.13, (x, 1.3+0.05*i, 0.83), D.mat([(0.15, 0.5, 0.2), (0.6, 0.6, 0.65), (0.1, 0.1, 0.12)][i], 0.3, 0.8), seg=14)
D.desk_lamp((0.35, 1.45, 0.76), (-0.3, 1.1, 0.76), energy=35)
A.model("Shelf_01", (1.8, 1.7, 0), rot_z=180, fit_height=1.8)
A.model("potted_plant_01", (-2.0, 1.8, 0), fit_height=0.9)
# Figur: tippt, lehnt sich am Ende zurueck
D.box((0.5, 0.5, 0.06), (-0.6, 0.5, 0.46), D.mat((0.08, 0.08, 0.09), 0.5)); D.box((0.5, 0.06, 0.6), (-0.6, 0.24, 0.8), D.mat((0.08, 0.08, 0.09), 0.5)); D.cyl(0.03, 0.44, (-0.6, 0.5, 0.22), D.mat((0.2, 0.2, 0.22), 0.3, 0.8))
J = D.figure((-0.6, 0.5, -0.42), rot=math.pi/2, shirt=(0.22, 0.24, 0.3), seed=77)
D.pose(J, 1, leg_l=(0, -88, 0), leg_r=(0, -88, 0), torso=(0, 12, 0), head=(0, 6, 0), arm_l=(0, -55, 8), fore_l=(0, -45, 0), arm_r=(0, -55, -8), fore_r=(0, -45, 0))
for f in range(1, int(F1*0.7), 8):
    D.pose(J, f, fore_l=(0, -45, 0), fore_r=(0, -40, 0)); D.pose(J, f+4, fore_l=(0, -40, 0), fore_r=(0, -46, 0))
D.pose(J, int(F1*0.85), torso=(0, -6, 0), head=(0, -4, 0), arm_l=(0, -20, 10), fore_l=(0, -20, 0), arm_r=(0, -20, -10), fore_r=(0, -20, 0))
D.sound("marker_write", 1, (-0.6, 1.15, 0.8), gain=0.15, ref=3)
D.dust((-1.3, 0.8, 0.8), (0.6, 1.6, 2.0), n=120, in_beam=0)
D.camera(lens=32)
D.camera_path([(1, (1.0, -0.4, 1.55), (-0.55, 1.45, 1.0)), (F1, (0.7, 0.0, 1.45), (-0.55, 1.5, 1.02))])
D.render(OUT, 1, F1, still=STILL)
