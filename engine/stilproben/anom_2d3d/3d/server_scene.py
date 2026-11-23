"""ANOM-Stilprobe: Serverraum, Kamera faehrt durch den Gang, LEDs blinken.
usage: python3 server_scene.py <outdir> [still]"""
import sys, os, math, random
sys.path.insert(0, "/home/claude/goldsmith-pipeline/engine/diorama")
import bpy
import dio as D
import assets as A
OUT = sys.argv[1]; STILL = int(sys.argv[2]) if len(sys.argv) > 2 else None
TEX = "/home/claude/anom/tex"
D.reset(res=(1280, 720), samples=int(os.environ.get("SAMPLES", "8")))
D.world_camera_only(cam_color=(0.0, 0.0, 0.0), light_color=(0.004, 0.006, 0.01))
r = random.Random(11)
floor = D.box((4, 12, 0.1), (0, 3, -0.05), A.texture("brushed_concrete", 0.8, tint=(0.35, 0.38, 0.42), rough_mul=0.35))
D.box((4, 12, 0.1), (0, 3, 2.75), D.mat((0.03, 0.035, 0.04), 0.8))
D.box((4, 0.1, 2.8), (0, 9, 1.4), D.mat((0.02, 0.022, 0.026), 0.7))

def tex_mat(path, name, emit=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True; N = m.node_tree.nodes
    t = N.new("ShaderNodeTexImage"); t.image = bpy.data.images.load(path); b = N["Principled BSDF"]
    m.node_tree.links.new(t.outputs["Color"], b.inputs["Base Color"]); b.inputs["Roughness"].default_value = 0.45; b.inputs["Metallic"].default_value = 0.6
    return m
fronts = [tex_mat(f"{TEX}/rack_{i}.png", f"rf{i}") for i in range(4)]

# LED-Materialien: Emission mit Rausch-Treiber (jede Gruppe blinkt anders)
def led_mat(color, base, amp, scale, phase):
    m = bpy.data.materials.new("led"); m.use_nodes = True; b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*color, 1); b.inputs["Emission Color"].default_value = (*color, 1)
    s = b.inputs["Emission Strength"]; s.default_value = base
    fc = s.driver_add("default_value"); fc.driver.expression = "0"
    fc.driver.type = "SCRIPTED"
    mod = fc.modifiers.new("NOISE"); mod.scale = scale; mod.strength = amp; mod.phase = phase; mod.offset = phase*3
    mod2 = fc.modifiers.new("GENERATOR"); mod2.coefficients = (base, 0.0); mod2.mode = "POLYNOMIAL"; mod2.use_additive = True
    return m
LED = []
for i in range(10):
    col = r.choice([(0.35, 0.95, 1.0)]*4 + [(0.3, 1.0, 0.5)]*3 + [(1.0, 0.65, 0.15)]*2 + [(1.0, 0.15, 0.1)])
    LED.append(led_mat(col, 5, 12, r.choice([1.5, 2.5, 4, 6]), r.random()*50))

def rack(x, y, face):
    """face = +1: Front zeigt nach +x, -1: nach -x"""
    D.box((0.62, 0.9, 2.1), (x, y, 1.05), D.mat((0.025, 0.027, 0.03), 0.35, 0.7), bevel=0.01)
    fx = x + face*0.312
    v = [(0, -0.42, -1.0), (0, 0.42, -1.0), (0, 0.42, 1.0), (0, -0.42, 1.0)]
    if face < 0: v = [v[1], v[0], v[3], v[2]]
    o = D.mesh_obj("front", v, [(0, 1, 2, 3)], r.choice(fronts)); o.location = (fx, y, 1.05)
    uv = o.data.uv_layers.new()
    for k, lp in enumerate(o.data.loops): uv.data[k].uv = [(0, 0), (1, 0), (1, 1), (0, 1)][lp.vertex_index] if face > 0 else [(1, 0), (0, 0), (0, 1), (1, 1)][lp.vertex_index]
    z = 0.12
    while z < 2.0:
        for j in range(r.randint(2, 6)):
            yy = y - 0.36 + j*0.03 + (0.0 if face > 0 else 0.0)
            D.box((0.006, 0.012, 0.008), (fx + face*0.004, yy, z), r.choice(LED))
        z += r.choice([0.076, 0.076, 0.152])
    # Griffe
    D.box((0.02, 0.02, 1.9), (fx + face*0.015, y + 0.38, 1.05), D.mat((0.3, 0.31, 0.33), 0.3, 1.0))

for i in range(7):
    rack(-0.95, i*0.92, +1); rack(0.95, i*0.92, -1)
# Deckenlichter: kalte Streifen, eines am Ende flackert
strip = D.mat((0.8, 0.9, 1.0), 0.3, emit=6, emit_color=(0.75, 0.88, 1.0))
for i in range(5):
    D.box((0.12, 1.2, 0.03), (0, i*1.6 + 0.4, 2.68), strip)
    D.area((0, i*1.6 + 0.4, 2.6), (0, i*1.6 + 0.4, 0), energy=55, color=(0.7, 0.85, 1.0), size=0.6)
# Kaltblaues Grundlicht + rotes Warnlicht am Gangende (Akzent)
D.area((0, 8.5, 1.5), (0, 0, 1.2), energy=30, color=(0.25, 0.45, 1.0), size=2.5)
warn = D.point((0.6, 8.6, 2.3), energy=8, color=(1.0, 0.1, 0.08), radius=0.05)
D.flicker(warn, 1, 120, 8, amp=0.9, seed=4)

cam = D.camera(24)
cam.data.dof.use_dof = True; cam.data.dof.aperture_fstop = 2.8; cam.data.dof.focus_distance = 2.2
F1 = 96
D.camera_path([(1, (0.18, -1.6, 1.25), (-0.1, 4.0, 1.15), 24), (F1, (0.05, 1.8, 1.4), (-0.55, 5.4, 1.1), 26)])
D.handheld(0.01, 1, F1)
D.SC.frame_step = int(os.environ.get("STEP", "2"))
if STILL: D.render(OUT, still=STILL)
else: D.render(OUT, 1, F1)
