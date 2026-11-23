"""ANOM-Stilprobe: Handy auf einem Tisch nachts. SHOT=hook (Bildschirm geht an, Kamera faehrt heran)
oder SHOT=end (Draufsicht, 'Verbindung getrennt', Bildschirm erlischt).
usage: SHOT=hook python3 phone_scene.py <outdir> [still]"""
import sys, os, math
sys.path.insert(0, "/home/claude/goldsmith-pipeline/engine/diorama")
import bpy
import dio as D
import assets as A
OUT = sys.argv[1]; STILL = int(sys.argv[2]) if len(sys.argv) > 2 else None
SHOT = os.environ.get("SHOT", "hook")
TEX = "/home/claude/anom/tex"
D.reset(res=(1280, 720), samples=int(os.environ.get("SAMPLES", "10")))
D.world_camera_only(cam_color=(0.01, 0.012, 0.02), cam_strength=1.0, light_color=(0.006, 0.008, 0.014), light_strength=1.0)
TZ = 0.76
# Raum
D.box((6, 6, 0.1), (0, 0, -0.05), A.texture("wood_floor_deck", 0.6, tint=(0.25, 0.2, 0.17)))
D.box((6, 0.12, 3), (0, 1.6, 1.5), A.texture("plastered_wall", 0.5, tint=(0.25, 0.27, 0.32)))
# Fenster mit Nachtstadt (unscharf im Hintergrund)
from PIL import Image, ImageDraw, ImageFilter
import random
r = random.Random(4); im = Image.new("RGB", (1200, 700), (8, 12, 24)); d = ImageDraw.Draw(im)
for b in range(22):
    x0 = r.randint(-40, 1150); w = r.randint(50, 150); h = r.randint(220, 680)
    d.rectangle([x0, 700-h, x0+w, 700], fill=(12, 14, 22))
    for yy in range(700-h+12, 690, 22):
        for xx in range(x0+6, x0+w-8, 15):
            if r.random() < 0.28: d.rectangle([xx, yy, xx+7, yy+11], fill=r.choice([(255, 196, 120), (200, 220, 255), (255, 170, 90)]))
im.save("/tmp/anom_city.png")
city = D.textured_plane("/tmp/anom_city.png", 3.2, 1.9, (-0.9, 1.53, 1.55), (0, 0, 0), emit=0.9); D.no_shadow(city)
D.box((3.3, 0.05, 0.05), (-0.9, 1.52, 2.5), D.mat((0.03, 0.03, 0.03))); D.box((0.05, 0.05, 2.0), (-0.9, 1.52, 1.55), D.mat((0.03, 0.03, 0.03)))
# Tisch (dunkles Holz)
top = D.box((1.6, 1.0, 0.05), (0, 0.1, TZ-0.025), A.texture("wood_floor_deck", 3.2, tint=(0.42, 0.3, 0.22), rough_mul=0.8), bevel=0.01)
for x in (-0.72, 0.72):
    for y in (-0.32, 0.52): D.box((0.06, 0.06, TZ-0.05), (x, y, (TZ-0.05)/2), D.mat((0.05, 0.035, 0.025), 0.6))

# Handy
body = D.box((0.078, 0.162, 0.009), (0, 0, TZ+0.0045), D.mat((0.012, 0.012, 0.014), 0.18, 0.6), rot=(0, 0, math.radians(-14)), bevel=0.006)
def screen_mat(path, name):
    m = bpy.data.materials.new(name); m.use_nodes = True; N = m.node_tree.nodes; L = m.node_tree.links
    b = N["Principled BSDF"]; t = N.new("ShaderNodeTexImage"); t.image = bpy.data.images.load(path)
    b.inputs["Base Color"].default_value = (0.004, 0.004, 0.005, 1); b.inputs["Roughness"].default_value = 0.08
    L.new(t.outputs["Color"], b.inputs["Emission Color"]); b.inputs["Emission Strength"].default_value = 0.0
    return m, b
scr_path = f"{TEX}/screen_chat.png" if SHOT == "hook" else f"{TEX}/screen_off.png"
sm, sb = screen_mat(scr_path, "screen")
v = [(-0.036, -0.076, 0), (0.036, -0.076, 0), (0.036, 0.076, 0), (-0.036, 0.076, 0)]
scr = D.mesh_obj("scr", v, [(0, 1, 2, 3)], sm); scr.location = (0, 0, TZ+0.0092); scr.rotation_euler = (0, 0, math.radians(-14))
uv = scr.data.uv_layers.new()
for i, lp in enumerate(scr.data.loops): uv.data[i].uv = [(0, 0), (1, 0), (1, 1), (0, 1)][lp.vertex_index]
glow = D.area((0, 0, TZ+0.05), (0, 0, TZ+1), energy=0.0, color=(1.0, 0.82, 0.55), size=0.12)
glow.rotation_euler = (math.pi, 0, 0)   # strahlt nach oben wie ein Bildschirm (Licht auf Gesicht/Umgebung)
gl2 = D.area((0, 0, TZ+0.012), (0, 0, TZ+0.3), energy=0.0, color=(1.0, 0.8, 0.5), size=0.1)

def screen_on(f_on, level=3.2, f_off=None):
    sb.inputs["Emission Strength"].default_value = 0.0; sb.inputs["Emission Strength"].keyframe_insert("default_value", frame=f_on-1)
    sb.inputs["Emission Strength"].default_value = level; sb.inputs["Emission Strength"].keyframe_insert("default_value", frame=f_on+2)
    for L, e in ((glow, 1.2), (gl2, 0.6)):
        L.data.energy = 0; L.data.keyframe_insert("energy", frame=f_on-1); L.data.energy = e; L.data.keyframe_insert("energy", frame=f_on+2)
    if f_off:
        sb.inputs["Emission Strength"].keyframe_insert("default_value", frame=f_off)
        sb.inputs["Emission Strength"].default_value = 0.0; sb.inputs["Emission Strength"].keyframe_insert("default_value", frame=f_off+3)
        for L, e in ((glow, 1.2), (gl2, 0.6)):
            L.data.keyframe_insert("energy", frame=f_off); L.data.energy = 0; L.data.keyframe_insert("energy", frame=f_off+3)

# Requisiten: zweites Handy (umgedreht), Geldbuendel, Schluessel, Aschenbecher, Becher, Notizblock
D.box((0.075, 0.155, 0.01), (0.26, 0.17, TZ+0.005), D.mat((0.03, 0.03, 0.035), 0.35, 0.3), rot=(0, 0, math.radians(31)), bevel=0.006)
nm = bpy.data.materials.new("note"); nm.use_nodes = True
nt = nm.node_tree.nodes.new("ShaderNodeTexImage"); nt.image = bpy.data.images.load(f"{TEX}/note.png")
nm.node_tree.links.new(nt.outputs["Color"], nm.node_tree.nodes["Principled BSDF"].inputs["Base Color"])
nm.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.85
for i, (x, y, rz) in enumerate([(-0.3, 0.18, 8), (-0.24, 0.12, -6), (-0.33, 0.06, 20)]):
    stack = D.box((0.156, 0.07, 0.022), (x, y, TZ+0.011+(0.022 if i == 1 else 0)), nm, rot=(0, 0, math.radians(rz)))
    tv = [(-0.078, -0.035, 0.0111), (0.078, -0.035, 0.0111), (0.078, 0.035, 0.0111), (-0.078, 0.035, 0.0111)]
    tp = D.mesh_obj("nt", tv, [(0, 1, 2, 3)], nm); tp.location = stack.location; tp.rotation_euler = stack.rotation_euler
    uvl = tp.data.uv_layers.new()
    for k, lp in enumerate(tp.data.loops): uvl.data[k].uv = [(0, 0), (1, 0), (1, 1), (0, 1)][lp.vertex_index]
    D.box((0.012, 0.072, 0.024), (x, y, stack.location.z), D.mat((0.55, 0.1, 0.08), 0.5), rot=(0, 0, math.radians(rz)))
D.torus(0.016, 0.003, (0.14, -0.15, TZ+0.003), D.mat((0.7, 0.7, 0.72), 0.25, 1.0))
D.box((0.06, 0.025, 0.012), (0.17, -0.18, TZ+0.006), D.mat((0.02, 0.02, 0.022), 0.4), rot=(0, 0, 0.6), bevel=0.004)
D.cyl(0.055, 0.025, (0.42, -0.05, TZ+0.0125), D.mat((0.6, 0.62, 0.66), 0.05, 0.0, alpha=1.0))
D.cyl(0.04, 0.1, (-0.5, -0.12, TZ+0.05), D.mat((0.05, 0.05, 0.06), 0.3, 0.2), seg=32)
D.box((0.15, 0.21, 0.008), (0.45, 0.25, TZ+0.004), D.mat((0.75, 0.72, 0.64), 0.9), rot=(0, 0, math.radians(-8)))
# Licht: Tischlampe links hinten (warm), Mondlicht vom Fenster (kalt)
D.desk_lamp((-0.62, 0.45, TZ), (0.0, 0.0, TZ), energy=7, color=(1, 0.68, 0.38))
D.area((-1.0, 1.3, 2.0), (0, 0, TZ), energy=26, color=(0.5, 0.62, 1.0), size=1.4)
D.area((1.4, -0.8, 1.6), (0, 0, TZ), energy=3, color=(0.6, 0.7, 1.0), size=1.0)

cam = D.camera(40)
cam.data.dof.use_dof = True; cam.data.dof.aperture_fstop = 2.2
foc = D.empty((0, 0, TZ+0.01), "focus"); cam.data.dof.focus_object = foc
if SHOT == "hook":
    F1 = 120
    D.camera_path([(1, (0.62, -0.78, 1.02), (0.0, 0.05, TZ), 34), (F1, (0.17, -0.27, 0.93), (0.0, 0.0, TZ), 46)])
    D.linear(cam) if False else None
    screen_on(28)
else:
    F1 = 72
    sb_level = 3.2
    D.camera_path([(1, (0.03, -0.06, 1.22), (0.0, 0.0, TZ), 50), (F1, (-0.02, 0.02, 1.08), (0.0, 0.0, TZ), 50)])
    cam.data.dof.aperture_fstop = 3.5
    sb.inputs["Emission Strength"].default_value = sb_level; sb.inputs["Emission Strength"].keyframe_insert("default_value", frame=1)
    glow.data.energy = 1.2; gl2.data.energy = 0.6
    glow.data.keyframe_insert("energy", frame=1); gl2.data.keyframe_insert("energy", frame=1)
    screen_on(1, f_off=46) if False else None
    sb.inputs["Emission Strength"].keyframe_insert("default_value", frame=44)
    sb.inputs["Emission Strength"].default_value = 0.0; sb.inputs["Emission Strength"].keyframe_insert("default_value", frame=48)
    for L in (glow, gl2):
        L.data.keyframe_insert("energy", frame=44); L.data.energy = 0; L.data.keyframe_insert("energy", frame=48)
D.handheld(0.004, 1, F1)
D.SC.frame_step = int(os.environ.get("STEP", "2"))
if STILL: D.render(OUT, still=STILL)
else: D.render(OUT, 1, F1)
