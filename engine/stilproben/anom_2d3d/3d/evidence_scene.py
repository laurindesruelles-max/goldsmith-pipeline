"""ANOM-Stilprobe: Beweismitteltisch nach der Razzia (Handys in Beuteln, Bargeld, Pakete, Etiketten).
usage: python3 evidence_scene.py <outdir> [still]"""
import sys, os, math, random
sys.path.insert(0, "/home/claude/goldsmith-pipeline/engine/diorama")
import bpy
import dio as D
import assets as A
OUT = sys.argv[1]; STILL = int(sys.argv[2]) if len(sys.argv) > 2 else None
TEX = "/home/claude/anom/tex"
D.reset(res=(1280, 720), samples=int(os.environ.get("SAMPLES", "8")))
D.world_camera_only(cam_color=(0.0, 0.0, 0.0), light_color=(0.01, 0.012, 0.016))
r = random.Random(5)
TZ = 0.9
D.box((8, 8, 0.1), (0, 0, -0.05), A.texture("brushed_concrete", 0.6, tint=(0.25, 0.26, 0.28)))
D.box((2.4, 1.3, 0.04), (0, 0, TZ-0.02), D.mat((0.22, 0.235, 0.25), 0.3, 0.85), bevel=0.008)
D.box((8, 0.1, 3), (0, 1.6, 1.5), A.texture("chipped_concrete", 0.5, tint=(0.22, 0.24, 0.28)))   # Metalltisch

def img_mat(path, rough=0.8):
    m = bpy.data.materials.new("im"); m.use_nodes = True; N = m.node_tree.nodes
    t = N.new("ShaderNodeTexImage"); t.image = bpy.data.images.load(path); b = N["Principled BSDF"]
    m.node_tree.links.new(t.outputs["Color"], b.inputs["Base Color"]); b.inputs["Roughness"].default_value = rough
    return m
def top_plane(m, w, h, loc, rz):
    v = [(-w/2, -h/2, 0), (w/2, -h/2, 0), (w/2, h/2, 0), (-w/2, h/2, 0)]
    o = D.mesh_obj("tp", v, [(0, 1, 2, 3)], m); o.location = loc; o.rotation_euler = (0, 0, rz)
    uv = o.data.uv_layers.new()
    for k, lp in enumerate(o.data.loops): uv.data[k].uv = [(0, 0), (1, 0), (1, 1), (0, 1)][lp.vertex_index]
    return o
note = img_mat(f"{TEX}/note.png"); brick = D.nmat((0.36, 0.25, 0.12), var=0.35, scale=9.0, rough=0.28, bump=0.5, stripes=True)
tags = [img_mat(f"{TEX}/tag{i}.png", 0.9) for i in (1, 2, 3)]
bag = D.mat((0.85, 0.88, 0.92), 0.05, 0.0, alpha=0.05)
scr_off = D.mat((0.01, 0.01, 0.012), 0.08, 0.3)
body = D.mat((0.02, 0.02, 0.024), 0.3, 0.5)

# Reihe 1: Handys in Beweisbeuteln mit Etikett
for i in range(6):
    x = -0.95 + i*0.36; y = 0.38 + r.uniform(-0.03, 0.03); rz = math.radians(r.uniform(-7, 7))
    D.box((0.075, 0.155, 0.009), (x, y, TZ+0.006), body, rot=(0, 0, rz), bevel=0.005)
    top_plane(scr_off, 0.068, 0.145, (x, y, TZ+0.0106), rz)
    D.box((0.2, 0.28, 0.004), (x, y-0.03, TZ+0.013), bag, rot=(0, 0, rz))
    D.box((0.2, 0.02, 0.006), (x, y+0.1, TZ+0.014), D.mat((0.85, 0.12, 0.1), 0.5), rot=(0, 0, rz))
    top_plane(tags[0], 0.13, 0.068, (x+0.02, y-0.12, TZ+0.016), rz + math.radians(r.uniform(-4, 4)))
# Reihe 2: Bargeld-Buendel in Stapeln
for s in range(3):
    bx = -0.7 + s*0.42
    for layer in range(r.randint(3, 5)):
        for k in range(2):
            x = bx + k*0.17 + r.uniform(-0.006, 0.006); y = -0.02 + r.uniform(-0.008, 0.008); z = TZ + 0.012 + layer*0.024
            rz = math.radians(r.uniform(-3, 3) + 90)
            D.box((0.156, 0.07, 0.022), (x, y, z), note, rot=(0, 0, rz))
            top_plane(note, 0.156, 0.07, (x, y, z+0.0111), rz)
            D.box((0.012, 0.072, 0.0235), (x, y, z), D.mat((0.6, 0.12, 0.08), 0.5), rot=(0, 0, rz))
top_plane(tags[1], 0.13, 0.068, (0.62, -0.1, TZ+0.002), math.radians(-6))
# Reihe 3: verklebte Pakete
for i in range(7):
    x = -0.9 + i*0.27; y = -0.4 + r.uniform(-0.02, 0.02); rz = math.radians(r.uniform(-8, 8))
    for layer in range(1 if i % 3 else 2):
        D.box((0.24, 0.13, 0.06), (x, y, TZ+0.03+layer*0.062), brick, rot=(0, 0, rz), bevel=0.012)
        D.box((0.035, 0.134, 0.064), (x, y, TZ+0.03+layer*0.062), D.mat((0.55, 0.56, 0.58), 0.25, 0.6), rot=(0, 0, rz))
top_plane(tags[2], 0.13, 0.068, (1.02, -0.32, TZ+0.002), math.radians(9))
# Maßstab + Nummernschilder (gelbe Dreiecke wie bei der Spurensicherung)
for i, (x, y) in enumerate([(-1.1, 0.55), (-1.05, -0.05), (-1.12, -0.42)]):
    v = [(-0.04, -0.03, 0), (0.04, -0.03, 0), (0.0, 0.03, 0.05)]
    o = D.mesh_obj("cone", [(-0.04, -0.025, 0), (0.04, -0.025, 0), (0.04, 0.025, 0), (-0.04, 0.025, 0), (0, 0, 0.06), (0, 0.0, 0.06)],
                   [(0, 1, 4), (2, 3, 5), (1, 2, 5, 4), (3, 0, 4, 5)], D.mat((1.0, 0.75, 0.05), 0.5))
    o.location = (x, y, TZ)
# Licht: kaltes Neon von oben, warmes Seitenlicht, Kamera-Blitz-Gefuehl
D.area((0, 0, TZ+1.6), (0, 0, TZ), energy=34, color=(0.85, 0.92, 1.0), size=1.2)
D.area((-1.8, -1.2, TZ+0.9), (0, 0, TZ), energy=25, color=(1.0, 0.75, 0.5), size=1.0)
D.area((1.8, 1.4, TZ+1.2), (0, 0, TZ), energy=10, color=(0.4, 0.55, 1.0), size=1.2)
flash = D.area((0.4, -0.9, TZ+1.3), (0, 0, TZ), energy=0, color=(1, 1, 1), size=0.4)
for f in (41, 87):   # zwei Kamerablitze der Spurensicherung
    flash.data.energy = 0; flash.data.keyframe_insert("energy", frame=f-1)
    flash.data.energy = 220; flash.data.keyframe_insert("energy", frame=f)
    flash.data.energy = 0; flash.data.keyframe_insert("energy", frame=f+2)

cam = D.camera(35)
cam.data.dof.use_dof = True; cam.data.dof.aperture_fstop = 4.0
foc = D.empty((0, 0, TZ), "focus"); cam.data.dof.focus_object = foc
D.key(foc, 1, loc=(-0.8, 0.3, TZ)); D.key(foc, 120, loc=(0.6, -0.1, TZ))
F1 = 120
D.camera_path([(1, (-1.15, -0.95, TZ+0.75), (-0.75, 0.15, TZ), 35), (F1, (0.55, -1.05, TZ+0.95), (0.5, 0.0, TZ), 32)])
D.handheld(0.006, 1, F1)
D.SC.frame_step = int(os.environ.get("STEP", "2"))
if STILL: D.render(OUT, still=STILL)
else: D.render(OUT, 1, F1)
