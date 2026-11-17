"""Goldsmith – Miniatur-Diorama-Bibliothek (Blender/bpy, Cycles CPU).

Wiederverwendbare Bausteine für die 3D-Szenen im VANTAGE-Stil (Modelleisenbahn-Look):
Sets (Gelände/Stadt, Straße, Innenraum), Häuser, Autos, Miniaturfiguren, Lampen,
Kamerafahrten, Lichtstrahl + Staub-Export für die 2D-Nachbearbeitung (post.py).

Pro Video schreibt Claude ein kurzes Szenen-Skript (Vorlagen: engine/diorama/scenes/*.py):
    import dio as D
    D.reset()                                   # 960x540, 24 fps, Cycles CPU
    ... Set bauen, Figuren/Autos animieren, D.camera_path([...]) ...
    D.render(OUT, frames)                       # PNGs + meta.json (Staub/Lichtstrahl je Frame)
Rendern: python3 scene.py <outdir>  (im Hintergrund mit nohup, NIE zwei Blender-Prozesse parallel)
Richtwert: 960x540, 8 Samples + Denoiser ≈ 4–8 s/Frame auf 2 Kernen.
"""
import bpy, bmesh, math, random, json, os
from mathutils import Vector, noise
from bpy_extras.object_utils import world_to_camera_view

FPS = 24
SC = None
BEAMS = []      # Lichtstrahlen für post.py
CUES = []       # Geräusche, die an Objekten im Bild hängen (cues.py mischt sie)
DUST = []       # Staubwolken für post.py


# ------------------------------------------------------------------ Grundlagen
def reset(res=(960, 540), samples=8, fps=FPS, world=(0.02, 0.025, 0.035), world_strength=1.0, exposure=0.0):
    global SC
    bpy.ops.wm.read_factory_settings(use_empty=True)
    p = bpy.context.preferences.edit
    p.keyframe_new_interpolation_type = "BEZIER"; p.keyframe_new_handle_type = "AUTO_CLAMPED"
    SC = bpy.context.scene
    SC.render.engine = "CYCLES"; SC.cycles.device = "CPU"
    SC.cycles.samples = samples; SC.cycles.use_denoising = True
    SC.cycles.max_bounces = 4; SC.cycles.diffuse_bounces = 2; SC.cycles.glossy_bounces = 2
    SC.cycles.transmission_bounces = 2; SC.cycles.volume_bounces = 0
    SC.cycles.light_sampling_threshold = 0.05
    SC.render.resolution_x, SC.render.resolution_y = res
    SC.render.fps = fps
    SC.view_settings.view_transform = "AgX"
    try: SC.view_settings.look = "AgX - Medium High Contrast"
    except Exception: pass
    SC.view_settings.exposure = exposure
    w = bpy.data.worlds.new("w"); SC.world = w; w.use_nodes = True
    bg = w.node_tree.nodes["Background"]; bg.inputs[0].default_value = (*world, 1); bg.inputs[1].default_value = world_strength
    BEAMS.clear(); DUST.clear(); CUES.clear()
    return SC


_MATS = {}
def mat(color, rough=0.6, metal=0.0, emit=0.0, emit_color=None, name=None, alpha=1.0):
    """Material (gecacht). color = (r,g,b) 0..1 linear."""
    k = (tuple(round(c, 3) for c in color), rough, metal, emit, emit_color, alpha)
    if k in _MATS and name is None: return _MATS[k]
    m = bpy.data.materials.new(name or f"m{len(_MATS)}"); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*color, 1)
    b.inputs["Roughness"].default_value = rough; b.inputs["Metallic"].default_value = metal
    if emit:
        b.inputs["Emission Color"].default_value = (*(emit_color or color), 1)
        b.inputs["Emission Strength"].default_value = emit
    if alpha < 1: b.inputs["Alpha"].default_value = alpha
    _MATS[k] = m
    return m


_NM = {}
def nmat(color, var=0.18, scale=6.0, rough=0.8, metal=0.0, bump=0.15, stripes=False):
    """Material mit Struktur (Putz, Holz, Beton): Farbvariation per Noise + leichte Unebenheit."""
    k = (tuple(round(c, 3) for c in color), var, scale, rough, metal, bump, stripes)
    if k in _NM: return _NM[k]
    m = bpy.data.materials.new(f"n{len(_NM)}"); m.use_nodes = True; nt = m.node_tree; N = nt.nodes; L = nt.links
    b = N["Principled BSDF"]; b.inputs["Roughness"].default_value = rough; b.inputs["Metallic"].default_value = metal
    tc = N.new("ShaderNodeTexCoord")
    nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = scale; nz.inputs["Detail"].default_value = 8
    if stripes:   # Holzmaserung: Noise in einer Richtung gestreckt
        mp = N.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (1, 1, 14)
        L.new(tc.outputs["Object"], mp.inputs[0]); L.new(mp.outputs[0], nz.inputs["Vector"])
    else:
        L.new(tc.outputs["Object"], nz.inputs["Vector"])
    cr = N.new("ShaderNodeValToRGB"); el = cr.color_ramp.elements
    el[0].position = 0.3; el[0].color = (*[c*(1-var) for c in color], 1)
    el[1].position = 0.7; el[1].color = (*[min(1, c*(1+var)) for c in color], 1)
    L.new(nz.outputs["Fac"], cr.inputs[0]); L.new(cr.outputs["Color"], b.inputs["Base Color"])
    if bump:
        bp = N.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = bump
        L.new(nz.outputs["Fac"], bp.inputs["Height"]); L.new(bp.outputs["Normal"], b.inputs["Normal"])
    _NM[k] = m
    return m


def no_shadow(*objs):
    for o in objs:
        o.visible_shadow = False
        for c in o.children: c.visible_shadow = False


def _link(o, coll=None):
    (coll or SC.collection).objects.link(o); return o


def mesh_obj(name, verts, faces, m=None, smooth=False):
    me = bpy.data.meshes.new(name); me.from_pydata(verts, [], faces); me.update()
    o = _link(bpy.data.objects.new(name, me))
    if m: o.data.materials.append(m)
    if smooth:
        for p in o.data.polygons: p.use_smooth = True
    return o


def box(size, loc, m=None, rot=(0, 0, 0), name="box", bevel=0.0):
    sx, sy, sz = [s/2 for s in size]
    v = [(-sx, -sy, -sz), (sx, -sy, -sz), (sx, sy, -sz), (-sx, sy, -sz), (-sx, -sy, sz), (sx, -sy, sz), (sx, sy, sz), (-sx, sy, sz)]
    f = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    o = mesh_obj(name, v, f, m); o.location = loc; o.rotation_euler = rot
    if bevel:
        b = o.modifiers.new("b", "BEVEL"); b.width = bevel; b.segments = 2
    return o


def cyl(r, h, loc, m=None, rot=(0, 0, 0), seg=24, name="cyl", r2=None, smooth=True):
    r2 = r if r2 is None else r2
    v = [(r*math.cos(2*math.pi*i/seg), r*math.sin(2*math.pi*i/seg), -h/2) for i in range(seg)]
    v += [(r2*math.cos(2*math.pi*i/seg), r2*math.sin(2*math.pi*i/seg), h/2) for i in range(seg)]
    f = [(i, (i+1) % seg, seg+(i+1) % seg, seg+i) for i in range(seg)]
    f += [tuple(reversed(range(seg))), tuple(range(seg, 2*seg))]
    o = mesh_obj(name, v, f, m); o.location = loc; o.rotation_euler = rot
    if smooth:
        for p in o.data.polygons[:seg]: p.use_smooth = True
    return o


def sphere(r, loc, m=None, seg=16, ring=10, name="sph", scale=(1, 1, 1)):
    v = [(0, 0, -r)]
    for j in range(1, ring):
        th = math.pi*j/ring - math.pi/2
        for i in range(seg):
            ph = 2*math.pi*i/seg; v.append((r*math.cos(th)*math.cos(ph), r*math.cos(th)*math.sin(ph), r*math.sin(th)))
    v.append((0, 0, r)); top = len(v)-1; f = []
    for i in range(seg): f.append((0, 1+(i+1) % seg, 1+i))
    for j in range(ring-2):
        for i in range(seg):
            a = 1+j*seg+i; b = 1+j*seg+(i+1) % seg; f.append((a, b, b+seg, a+seg))
    base = 1+(ring-2)*seg
    for i in range(seg): f.append((base+i, base+(i+1) % seg, top))
    o = mesh_obj(name, v, f, m, smooth=True); o.location = loc; o.scale = scale
    return o


def empty(loc=(0, 0, 0), name="e"):
    e = _link(bpy.data.objects.new(name, None)); e.location = loc; return e


def parent(child, par):
    """Kind behält seine Koordinaten als LOKALE Koordinaten relativ zum Elternobjekt."""
    child.parent = par; return child


def torus(R, r, loc, m=None, rot=(0, 0, 0), seg=24, sseg=8, name="torus", scale=(1, 1, 1)):
    v = []; f = []
    for i in range(seg):
        a = 2*math.pi*i/seg
        for j in range(sseg):
            b = 2*math.pi*j/sseg; rr = R + r*math.cos(b)
            v.append((rr*math.cos(a), rr*math.sin(a), r*math.sin(b)))
    for i in range(seg):
        for j in range(sseg):
            a0 = i*sseg+j; a1 = i*sseg+(j+1) % sseg; b0 = ((i+1) % seg)*sseg+j; b1 = ((i+1) % seg)*sseg+(j+1) % sseg
            f.append((a0, b0, b1, a1))
    o = mesh_obj(name, v, f, m, smooth=True); o.location = loc; o.rotation_euler = rot; o.scale = scale
    return o


def glasses(loc, rot=0.0, color=(0.05, 0.04, 0.035), metal=False, size=1.0):
    """Brillengestell (zwei Ringe + Steg), liegend."""
    m = mat(color, 0.25, 1.0 if metal else 0.0); root = empty(loc, "glasses"); root.rotation_euler = (0, 0, rot); s = size
    for x in (-0.032*s, 0.032*s):
        o = torus(0.025*s, 0.0035*s, (x, 0, 0.004*s), m, scale=(1, 0.8, 1)); parent(o, root)
    b = box((0.016*s, 0.004*s, 0.004*s), (0, 0.012*s, 0.006*s), m); parent(b, root)
    return root


def world_camera_only(cam_color=(1.0, 0.8, 0.55), cam_strength=1.0, light_color=(0.02, 0.025, 0.035), light_strength=1.0):
    """Hintergrund: Kamera sieht cam_color (z.B. Himmel hinter dem Fenster), Licht kommt nur von light_color."""
    w = SC.world; nt = w.node_tree; N = nt.nodes; L = nt.links
    bg = N["Background"]; out = N["World Output"]
    lp = N.new("ShaderNodeLightPath"); b2 = N.new("ShaderNodeBackground"); mx = N.new("ShaderNodeMixShader")
    bg.inputs[0].default_value = (*light_color, 1); bg.inputs[1].default_value = light_strength
    b2.inputs[0].default_value = (*cam_color, 1); b2.inputs[1].default_value = cam_strength
    L.new(lp.outputs["Is Camera Ray"], mx.inputs[0]); L.new(bg.outputs[0], mx.inputs[1]); L.new(b2.outputs[0], mx.inputs[2])
    L.new(mx.outputs[0], out.inputs[0])


def key(o, frame, loc=None, rot=None, scale=None, interp=None):
    if loc is not None: o.location = loc; o.keyframe_insert("location", frame=frame)
    if rot is not None: o.rotation_euler = rot; o.keyframe_insert("rotation_euler", frame=frame)
    if scale is not None: o.scale = scale; o.keyframe_insert("scale", frame=frame)
    if interp:
        ad = o.animation_data
        if ad and ad.action:
            for fc in _fcurves(ad.action):
                for kp in fc.keyframe_points: kp.interpolation = interp


def _fcurves(action):
    """Blender 5: Aktionen haben Layer/Strips/Channelbags; ältere: action.fcurves."""
    if hasattr(action, "fcurves"):
        try: return list(action.fcurves)
        except Exception: pass
    out = []
    for lay in getattr(action, "layers", []):
        for st in lay.strips:
            for cb in getattr(st, "channelbags", []): out += list(cb.fcurves)
    return out


def linear(o):
    if o.animation_data and o.animation_data.action:
        for fc in _fcurves(o.animation_data.action):
            for kp in fc.keyframe_points: kp.interpolation = "LINEAR"


# ------------------------------------------------------------------ Licht
def sun(rot=(math.radians(50), 0, math.radians(30)), energy=3.0, color=(1.0, 0.85, 0.65), angle=2.0):
    l = bpy.data.lights.new("sun", "SUN"); l.energy = energy; l.color = color; l.angle = math.radians(angle)
    o = _link(bpy.data.objects.new("sun", l)); o.rotation_euler = rot; return o


def point(loc, energy=50, color=(1, 0.75, 0.45), radius=0.05):
    l = bpy.data.lights.new("pt", "POINT"); l.energy = energy; l.color = color; l.shadow_soft_size = radius
    o = _link(bpy.data.objects.new("pt", l)); o.location = loc; return o


def spot(loc, target, energy=300, color=(1, 0.8, 0.55), size=60, blend=0.4, radius=0.05):
    l = bpy.data.lights.new("spot", "SPOT"); l.energy = energy; l.color = color
    l.spot_size = math.radians(size); l.spot_blend = blend; l.shadow_soft_size = radius
    o = _link(bpy.data.objects.new("spot", l)); o.location = loc; look_at(o, target); return o


def area(loc, target, energy=200, color=(1, 0.85, 0.7), size=2.0):
    l = bpy.data.lights.new("area", "AREA"); l.energy = energy; l.color = color; l.size = size
    o = _link(bpy.data.objects.new("area", l)); o.location = loc; look_at(o, target); return o


def look_at(o, target):
    d = Vector(target) - Vector(o.location); o.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()


def sound(name, f0, target, f1=None, gain=1.0, loop=False, ref=8.0, align="start"):
    """Geräusch an ein Objekt/eine Position hängen. name = Datei in assets/sfx (ohne .wav).
    f0/f1 = Start-/Endframe (f1 nur bei loop). target = Objekt (folgt ihm) oder (x,y,z).
    Lautstärke folgt automatisch der Entfernung zur Kamera (ref = Abstand mit voller Lautstärke),
    Stereo-Position folgt der Bildposition.
    align: "start" (Geräusch beginnt bei f0), "end" (endet bei f0, z.B. Auto hält an), "center" (z.B. Vorbeifahrt)."""
    CUES.append({"name": name, "f0": f0, "f1": f1 if f1 is not None else f0, "target": target, "gain": gain, "loop": loop, "ref": ref, "align": align})


def flicker(light_obj, f0, f1, base, amp=0.35, seed=1):
    """Licht flackert (Neon, Glühbirne)."""
    rnd = random.Random(seed); d = light_obj.data
    for f in range(f0, f1+1, 2):
        d.energy = base*(1-amp*rnd.random()**3); d.keyframe_insert("energy", frame=f)


# ------------------------------------------------------------------ Kamera
CAM = None
def camera(lens=50, sensor=36):
    global CAM
    c = bpy.data.cameras.new("cam"); c.lens = lens; c.sensor_width = sensor; c.clip_start = 0.05; c.clip_end = 5000
    CAM = _link(bpy.data.objects.new("cam", c)); SC.camera = CAM
    tgt = empty(name="cam_target"); tc = CAM.constraints.new("TRACK_TO"); tc.target = tgt
    tc.track_axis = "TRACK_NEGATIVE_Z"; tc.up_axis = "UP_Y"
    CAM["tgt"] = tgt.name
    return CAM


def camera_path(keys, lens=None):
    """keys: [(frame, (x,y,z) Kamera, (x,y,z) Blickziel[, lens])]. Weiche Bezier-Fahrt."""
    tgt = bpy.data.objects[CAM["tgt"]]
    for k in keys:
        f, loc, tg = k[0], k[1], k[2]
        key(CAM, f, loc=loc); key(tgt, f, loc=tg)
        if len(k) > 3: CAM.data.lens = k[3]; CAM.data.keyframe_insert("lens", frame=f)


def handheld(amount=0.02, f0=1, f1=240, seed=3):
    """leichtes Atmen der Kamera (wie gefilmtes Modell)."""
    tgt = bpy.data.objects[CAM["tgt"]]
    d = tgt.driver_add("delta_location")
    for i, fc in enumerate(d):
        n = fc.modifiers.new("NOISE"); n.scale = 60; n.strength = amount; n.phase = seed*7+i*13


# ------------------------------------------------------------------ Bausteine
WALLS = [(0.80, 0.74, 0.62), (0.70, 0.62, 0.52), (0.86, 0.80, 0.70), (0.62, 0.55, 0.47), (0.75, 0.66, 0.55), (0.55, 0.50, 0.46)]
ROOFS = [(0.42, 0.18, 0.12), (0.35, 0.16, 0.11), (0.28, 0.24, 0.22), (0.48, 0.25, 0.16)]


def house(loc, w=6, d=5, h=5, rot=0.0, wall=None, roof=None, lit=0.25, seed=0, win_color=(1.0, 0.62, 0.28), floors=None, flat=False):
    """Haus mit Satteldach und Fenstern (lit = Anteil beleuchteter Fenster)."""
    rnd = random.Random(seed); wall = wall or rnd.choice(WALLS); roof = roof or rnd.choice(ROOFS)
    root = empty(loc, "house"); root.rotation_euler = (0, 0, rot)
    b = box((w, d, h), (0, 0, h/2), mat(wall, 0.85)); parent(b, root); b.location = (0, 0, h/2)
    if flat:
        r = box((w+0.3, d+0.3, 0.3), (0, 0, h+0.15), mat(roof, 0.8)); parent(r, root); r.location = (0, 0, h+0.15)
    else:
        rh = min(w, d)*0.38; v = [(-w/2-0.3, -d/2-0.3, h), (w/2+0.3, -d/2-0.3, h), (w/2+0.3, d/2+0.3, h), (-w/2-0.3, d/2+0.3, h), (-w/2-0.3, 0, h+rh), (w/2+0.3, 0, h+rh)]
        f = [(0, 1, 5, 4), (2, 3, 4, 5), (0, 4, 3), (1, 2, 5), (0, 3, 2, 1)]
        r = mesh_obj("roof", v, f, mat(roof, 0.8)); parent(r, root); r.location = (0, 0, 0)
    floors = floors or max(1, int(h/2.6)); dark = mat((0.05, 0.05, 0.06), 0.3)
    litm = mat(win_color, 0.5, emit=4.0); out = []
    for side, (nx, ny, span, depth) in enumerate([(0, -1, w, d), (0, 1, w, d), (-1, 0, d, w), (1, 0, d, w)]):
        cols = max(1, int(span/1.8))
        for fl in range(floors):
            for c in range(cols):
                u = -span/2 + span*(c+0.5)/cols; z = 1.3 + fl*2.6
                if z+0.6 > h: continue
                m = litm if rnd.random() < lit else dark
                if nx == 0: o = box((0.8, 0.06, 1.0), (u, ny*(depth/2+0.02), z), m)
                else: o = box((0.06, 0.8, 1.0), (nx*(depth/2+0.02), u, z), m)
                parent(o, root); o.location = (u if nx == 0 else nx*(depth/2+0.02), ny*(depth/2+0.02) if nx == 0 else u, z)
                out.append(o)
    root["windows"] = len(out)
    return root


def tree(loc, h=4.0, seed=0, color=None):
    rnd = random.Random(seed); color = color or rnd.choice([(0.08, 0.16, 0.06), (0.1, 0.2, 0.07), (0.06, 0.13, 0.05)])
    t = cyl(0.12*h/4, h*0.3, (loc[0], loc[1], loc[2]+h*0.15), mat((0.18, 0.11, 0.06), 0.9), seg=8)
    if rnd.random() < 0.6:   # Nadelbaum
        c = cyl(h*0.22, h*0.8, (loc[0], loc[1], loc[2]+h*0.6), mat(color, 0.9), seg=10, r2=0.02)
    else:
        c = sphere(h*0.28, (loc[0], loc[1], loc[2]+h*0.65), mat(color, 0.9), seg=10, ring=7, scale=(1, 1, 1.15))
    return c


def car(loc, rot=0.0, color=(0.15, 0.2, 0.32), lights=False, name="car", length=4.6):
    """Kleines Auto (Limousine 60er–90er). Gibt Wurzel-Empty zurück (animierbar)."""
    s = length/4.6; root = empty(loc, name); root.rotation_euler = (0, 0, rot)
    paint = mat(color, 0.25, 0.3); glass = mat((0.015, 0.018, 0.022), 0.18, 0.2); chrome = mat((0.8, 0.8, 0.82), 0.15, 1.0)
    tire = mat((0.02, 0.02, 0.02), 0.7)
    def cabin(x0, x1, xt0, xt1, y, z0, z1, m):
        v = [(x0, -y, z0), (x1, -y, z0), (x1, y, z0), (x0, y, z0), (xt0, -y*0.92, z1), (xt1, -y*0.92, z1), (xt1, y*0.92, z1), (xt0, y*0.92, z1)]
        f = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
        return mesh_obj("cabin", v, f, m)
    body = box((4.6*s, 1.8*s, 0.62*s), (0, 0, 0.58*s), paint, bevel=0.12*s)
    parts = [body,
             cabin(-1.5*s, 0.85*s, -1.15*s, 0.25*s, 0.86*s, 0.88*s, 1.42*s, glass),
             box((1.42*s, 1.6*s, 0.07*s), (-0.45*s, 0, 1.45*s), paint, bevel=0.03*s),
             box((4.4*s, 1.84*s, 0.05*s), (0, 0, 0.78*s), chrome),
             box((0.06*s, 1.7*s, 0.18*s), (2.31*s, 0, 0.45*s), chrome), box((0.06*s, 1.7*s, 0.18*s), (-2.31*s, 0, 0.45*s), chrome)]
    for x in (-1.45, 1.45):
        for y in (-0.85, 0.85):
            parts.append(cyl(0.34*s, 0.24*s, (x*s, y*s, 0.34*s), tire, rot=(math.pi/2, 0, 0), seg=16))
    hl = mat((1, 0.92, 0.75), 0.2, emit=12.0 if lights else 0.0); tl = mat((0.8, 0.05, 0.03), 0.3, emit=5.0 if lights else 0.0)
    for y in (-0.6, 0.6):
        parts.append(box((0.05*s, 0.3*s, 0.16*s), (2.33*s, y*s, 0.62*s), hl)); parts.append(box((0.05*s, 0.3*s, 0.14*s), (-2.33*s, y*s, 0.62*s), tl))
    for p in parts:
        lp = p.location.copy(); parent(p, root); p.location = lp; p.rotation_euler = p.rotation_euler
    if lights:
        for y in (-0.6, 0.6):
            sp = bpy.data.lights.new("hl", "SPOT"); sp.energy = 120*s; sp.spot_size = math.radians(55); sp.spot_blend = 0.6; sp.color = (1, 0.88, 0.7)
            so = _link(bpy.data.objects.new("hl", sp)); so.parent = root; so.location = (2.4*s, y*s, 0.62*s); so.rotation_euler = (0, math.radians(97), 0)
    return root


def drive(obj, f0, f1, p0, p1, ease_in=True, ease_out=True, snd=True):
    """Auto fährt von p0 nach p1 (hält am Ende an). Hängt automatisch Motorgeräusch an (snd=False = stumm)."""
    key(obj, f0, loc=p0); key(obj, f1, loc=p1)
    if snd:   # Ankunft mit Anhalten -> Geräusch endet beim Halt; sonst Vorbeifahrt in der Mitte
        if ease_out: sound("car_arrive", f1+6, obj, gain=0.9, ref=10, align="end")
        else: sound("car_pass", (f0+f1)//2, obj, gain=0.9, ref=10, align="center")
    if obj.animation_data and obj.animation_data.action:
        for fc in _fcurves(obj.animation_data.action):
            for kp in fc.keyframe_points:
                kp.interpolation = "BEZIER"
                if not ease_in and kp.co[0] == f0: kp.interpolation = "LINEAR"


SKIN = [(0.72, 0.5, 0.38), (0.6, 0.4, 0.3), (0.8, 0.6, 0.47), (0.45, 0.3, 0.22)]
CLOTH = [(0.12, 0.13, 0.15), (0.2, 0.17, 0.13), (0.3, 0.27, 0.22), (0.1, 0.12, 0.18), (0.42, 0.38, 0.32), (0.55, 0.52, 0.47), (0.16, 0.1, 0.08)]


def figure(loc, rot=0.0, shirt=None, pants=None, skin=None, hair=(0.05, 0.035, 0.025), h=1.78, coat=False, hat=False, apron=None, seed=0, name="fig"):
    """Miniaturfigur im Modellbau-Stil (gedeckte, realistische Farben – keine Mannequins).
    Rückgabe dict: root, torso, head, arm_l, arm_r, leg_l, leg_r (Gelenk-Empties zum Animieren)."""
    rnd = random.Random(seed); s = h/1.78
    shirt = shirt or rnd.choice(CLOTH); pants = pants or rnd.choice(CLOTH[:4]); skin = skin or rnd.choice(SKIN)
    M = lambda c, r=0.75: mat(c, r)
    root = empty(loc, name); root.rotation_euler = (0, 0, rot)
    J = {"root": root}
    def joint(nm, pos, par):
        e = empty(name=f"{name}_{nm}"); e.parent = par; e.location = pos; J[nm] = e; return e
    hip = joint("hip", (0, 0, 0.92*s), root)
    for side, y in (("l", 0.1*s), ("r", -0.1*s)):
        lg = joint(f"leg_{side}", (0, y, 0), hip)
        p = cyl(0.06*s, 0.86*s, (0, 0, -0.43*s), M(pants), seg=14, r2=0.08*s); p.parent = lg; p.location = (0, 0, -0.45*s)
        sh = box((0.24*s, 0.1*s, 0.08*s), (0.05*s, 0, -0.9*s), M((0.06, 0.05, 0.045), 0.4), bevel=0.02*s); sh.parent = lg; sh.location = (0.05*s, 0, -0.88*s)
    torso = joint("torso", (0, 0, 0), hip)
    tl = 0.68*s if not coat else 0.95*s
    t = cyl(0.165*s, 0.5*s, (0, 0, 0.3*s), M(shirt), seg=20, r2=0.19*s); t.parent = torso; t.location = (0, 0, 0.27*s); t.scale = (0.68, 1, 1)
    sho = sphere(0.19*s, (0, 0, 0.52*s), M(shirt), seg=20, ring=10, scale=(0.68, 1.12, 0.55)); sho.parent = torso; sho.location = (0, 0, 0.52*s)
    belt = cyl(0.168*s, 0.05*s, (0, 0, 0.03*s), M((0.07, 0.05, 0.04), 0.5), seg=20); belt.parent = torso; belt.location = (0, 0, 0.03*s); belt.scale = (0.7, 1, 1)
    hips = sphere(0.165*s, (0, 0, 0.0), M(pants), seg=16, ring=8, scale=(0.72, 1.0, 0.45)); hips.parent = torso; hips.location = (0, 0, -0.01*s)
    if coat:
        c = cyl(0.21*s, tl, (0, 0, 0.0), M(shirt), seg=16, r2=0.2*s); c.parent = torso; c.location = (0, 0, 0.62*s - tl/2); c.scale = (0.78, 1, 1)
    if apron:
        a = box((0.03*s, 0.32*s, 0.75*s), (0.14*s, 0, 0.05*s), M(apron, 0.9)); a.parent = torso; a.location = (0.155*s, 0, 0.12*s)
    neck = cyl(0.05*s, 0.1*s, (0, 0, 0.66*s), M(skin), seg=10); neck.parent = torso; neck.location = (0, 0, 0.66*s)
    head = joint("head", (0, 0, 0.72*s), torso)
    hd = sphere(0.11*s, (0, 0, 0.1*s), M(skin, 0.6), seg=16, ring=10, scale=(1.0, 0.9, 1.15)); hd.parent = head; hd.location = (0, 0, 0.11*s)
    hr = sphere(0.115*s, (0, 0, 0.13*s), M(hair, 0.8), seg=16, ring=10, scale=(1.02, 0.95, 1.0)); hr.parent = head; hr.location = (-0.015*s, 0, 0.14*s)
    if hat:
        b1 = cyl(0.17*s, 0.015*s, (0, 0, 0.22*s), M(hat if isinstance(hat, tuple) else (0.1, 0.09, 0.08)), seg=20); b1.parent = head; b1.location = (0, 0, 0.21*s)
        b2 = cyl(0.11*s, 0.12*s, (0, 0, 0.28*s), M(hat if isinstance(hat, tuple) else (0.1, 0.09, 0.08)), seg=20); b2.parent = head; b2.location = (0, 0, 0.27*s)
    for side, y in (("l", 0.215*s), ("r", -0.215*s)):
        ar = joint(f"arm_{side}", (0, y*0.93, 0.58*s), torso)
        sp = sphere(0.05*s, (0, 0, 0), M(shirt), seg=12, ring=8); sp.parent = ar; sp.location = (0, 0, 0)
        u = cyl(0.05*s, 0.33*s, (0, 0, -0.16*s), M(shirt), seg=10, r2=0.055*s); u.parent = ar; u.location = (0, 0, -0.16*s)
        fo = joint(f"fore_{side}", (0, 0, -0.32*s), ar)
        lw = cyl(0.04*s, 0.3*s, (0, 0, -0.14*s), M(shirt), seg=10, r2=0.048*s); lw.parent = fo; lw.location = (0, 0, -0.14*s)
        hn = sphere(0.045*s, (0, 0, -0.31*s), M(skin, 0.6), seg=10, ring=6); hn.parent = fo; hn.location = (0, 0, -0.31*s)
    return J


def pose(J, frame, **rots):
    """pose(J, 12, arm_r=(0,-70,0), fore_r=(0,-40,0), head=(0,10,0))  – Grad, Euler XYZ (lokal)."""
    for k, r in rots.items():
        key(J[k], frame, rot=tuple(math.radians(a) for a in r))


def walk(J, f0, f1, p0, p1, step=14, snd="footsteps_street"):
    """Figur geht von p0 nach p1 (Beine/Arme schwingen). snd = Schrittgeräusch (None = stumm;
    "footsteps_wood" für Innenräume)."""
    if snd: sound(snd, f0, J["root"], f1=f1, loop=True, gain=0.7, ref=5)
    key(J["root"], f0, loc=p0); key(J["root"], f1, loc=p1); linear(J["root"])
    for i, f in enumerate(range(f0, f1+1, step)):
        a = 22 if i % 2 == 0 else -22
        pose(J, f, leg_l=(0, a, 0), leg_r=(0, -a, 0), arm_l=(0, -a*0.8, 0), arm_r=(0, a*0.8, 0))
    pose(J, f1+6, leg_l=(0, 0, 0), leg_r=(0, 0, 0), arm_l=(0, 0, 0), arm_r=(0, 0, 0))


# ------------------------------------------------------------------ Sets
def terrain(size=900, res=160, valley=55, peak=170, seed=4, snow=0.62, river=True):
    """Bergtal (z.B. Dolomiten): Talboden bei z≈0, Berge an den Seiten, Schnee auf den Gipfeln."""
    v = []; f = []
    for j in range(res+1):
        for i in range(res+1):
            x = -size/2 + size*i/res; y = -size/2 + size*j/res
            d = max(0.0, abs(x + 25*math.sin(y/90)) - valley)
            hgt = (d/ (size/2-valley))**1.25 * peak
            n = noise.fractal(Vector((x/120, y/120, seed)), 0.6, 2.2, 5)
            hgt += (8 + 0.45*hgt) * n + 1.5*noise.noise(Vector((x/15, y/15, seed+3)))
            v.append((x, y, max(hgt, 0.0) if d > 0 else 0.4*noise.noise(Vector((x/40, y/40, seed)))))
    for j in range(res):
        for i in range(res):
            a = j*(res+1)+i; f.append((a, a+1, a+res+2, a+res+1))
    o = mesh_obj("terrain", v, f)
    for p in o.data.polygons: p.use_smooth = True
    m = bpy.data.materials.new("terrain"); m.use_nodes = True; nt = m.node_tree; N = nt.nodes
    b = N["Principled BSDF"]; b.inputs["Roughness"].default_value = 0.95
    geo = N.new("ShaderNodeNewGeometry"); sep = N.new("ShaderNodeSeparateXYZ"); mr = N.new("ShaderNodeMapRange")
    mr.inputs[1].default_value = 0; mr.inputs[2].default_value = peak
    cr = N.new("ShaderNodeValToRGB"); el = cr.color_ramp.elements
    el[0].position = 0.0; el[0].color = (0.09, 0.15, 0.05, 1); el[1].position = 1.0; el[1].color = (0.92, 0.93, 0.95, 1)
    for pos, col in [(0.1, (0.11, 0.17, 0.06, 1)), (0.22, (0.07, 0.12, 0.05, 1)), (0.34, (0.2, 0.21, 0.13, 1)), (0.45, (0.32, 0.29, 0.25, 1)), (snow-0.02, (0.42, 0.4, 0.37, 1)), (snow+0.04, (0.85, 0.86, 0.88, 1))]:
        e = el.new(pos); e.color = col
    nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 0.08
    mix = N.new("ShaderNodeMath"); mix.operation = "MULTIPLY_ADD"; mix.inputs[1].default_value = 0.12
    L = nt.links
    L.new(geo.outputs["Position"], sep.inputs[0]); L.new(sep.outputs["Z"], mr.inputs[0])
    L.new(nz.outputs["Fac"], mix.inputs[0]); L.new(mr.outputs[0], mix.inputs[2]); L.new(mix.outputs[0], cr.inputs[0])
    L.new(cr.outputs["Color"], b.inputs["Base Color"])
    o.data.materials.append(m)
    if river:
        pts = [(-25*math.sin(y/90)+6, y) for y in range(-size//2, size//2+1, 10)]
        rv = []; rf = []
        for k, (x, y) in enumerate(pts):
            rv += [(x-4, y, 0.15), (x+4, y, 0.15)]
            if k: rf.append((2*k-2, 2*k-1, 2*k+1, 2*k))
        mesh_obj("river", rv, rf, mat((0.05, 0.09, 0.1), 0.05, 0.2))
    return o


def valley_x(y):
    return -25*math.sin(y/90)


def road(points, width=6, z=0.2, color=(0.09, 0.09, 0.095), name="road"):
    v = []; f = []
    for k, (x, y) in enumerate(points):
        if k < len(points)-1: dx, dy = points[k+1][0]-x, points[k+1][1]-y
        else: dx, dy = x-points[k-1][0], y-points[k-1][1]
        l = math.hypot(dx, dy) or 1; nx, ny = -dy/l*width/2, dx/l*width/2
        v += [(x+nx, y+ny, z), (x-nx, y-ny, z)]
        if k: f.append((2*k-2, 2*k-1, 2*k+1, 2*k))
    return mesh_obj(name, v, f, mat(color, 0.85))


def town(center=(0, 0), n=55, spread=70, seed=7, lit=0.3, along_valley=True):
    """Kleinstadt im Tal: Häuser entlang einer Straße, Bäume dazwischen."""
    rnd = random.Random(seed); houses = []
    cx, cy = center
    for i in range(n):
        y = cy + rnd.uniform(-spread*1.6, spread*1.6); x = (valley_x(y) if along_valley else cx) + rnd.choice([-1, 1])*rnd.uniform(10, spread*0.55)
        if any(math.hypot(x-hx, y-hy) < 9 for hx, hy in [(h.location.x, h.location.y) for h in houses]): continue
        w, d, h = rnd.uniform(5, 9), rnd.uniform(5, 8), rnd.uniform(4.5, 9)
        houses.append(house((x, y, 0), w, d, h, rot=math.radians(rnd.choice([0, 90, 3, -4, 88])), lit=lit, seed=i+seed*100))
    for i in range(n*2):
        y = cy + rnd.uniform(-spread*2.2, spread*2.2); x = valley_x(y) + rnd.choice([-1, 1])*rnd.uniform(14, spread*0.9)
        if any(math.hypot(x-h.location.x, y-h.location.y) < 7 for h in houses): continue
        tree((x, y, 0), rnd.uniform(4, 9), seed=i)
    road([(valley_x(y)-14, y) for y in range(int(cy-spread*2.5), int(cy+spread*2.5), 8)], width=6)
    return houses


def room(w=6.0, d=5.0, h=3.2, wall=(0.55, 0.48, 0.4), floor=(0.24, 0.16, 0.1), window=None, back_wall=True, left_wall=True, wall_mat=None, floor_mat=None):
    """Aufgeschnittener Innenraum (Diorama): Boden, Rückwand (y=+d/2), linke Wand (x=-w/2).
    window = dict(wall='back'|'left', u=Mitte, z=Unterkante, w=Breite, h=Höhe) -> Öffnung + Fensterkreuz."""
    fm = floor_mat or nmat(floor, 0.25, 3.0, 0.5, stripes=True); wm = wall_mat or nmat(wall, 0.12, 2.5, 0.95, bump=0.25)
    box((w, d, 0.1), (0, 0, -0.05), fm, name="floor")
    for i in range(int(w/0.25)):
        box((0.01, d, 0.002), (-w/2+i*0.25, 0, 0.001), mat((floor[0]*0.6, floor[1]*0.6, floor[2]*0.6), 0.7))
    def wall_with_hole(axis, length, pos):
        if not window or window["wall"] != axis:
            if axis == "back": box((w, 0.12, h), (0, d/2, h/2), wm, name="wall_b")
            else: box((0.12, d, h), (-w/2, 0, h/2), wm, name="wall_l")
            return
        u, z0, ww, wh = window["u"], window["z"], window["w"], window["h"]
        a0, a1 = -length/2, length/2
        segs = [((a0+u-ww/2)/2, 0, (u-ww/2)-a0, h), ((u+ww/2+a1)/2, 0, a1-(u+ww/2), h),
                (u, 0, ww, z0), (u, 0, ww, h-(z0+wh))]
        zs = [h/2, h/2, z0/2, z0+wh+(h-z0-wh)/2]
        for (cu, _, L, H), cz in zip(segs, zs):
            if L <= 0 or H <= 0: continue
            if axis == "back": box((L, 0.12, H), (cu, d/2, cz), wm)
            else: box((0.12, L, H), (-w/2, cu, cz), wm)
        frm = mat((0.18, 0.12, 0.08), 0.6)
        if axis == "back":
            box((ww, 0.06, 0.05), (u, d/2, z0+wh/2), frm); box((0.05, 0.06, wh), (u, d/2, z0+wh/2), frm)
            box((ww+0.1, 0.25, 0.06), (u, d/2-0.08, z0), frm)
        else:
            box((0.06, ww, 0.05), (-w/2, u, z0+wh/2), frm); box((0.06, 0.05, wh), (-w/2, u, z0+wh/2), frm)
            box((0.25, ww+0.1, 0.06), (-w/2+0.08, u, z0), frm)
    if back_wall: wall_with_hole("back", w, d/2)
    if left_wall: wall_with_hole("left", d, -w/2)
    # Sockelleiste
    box((w, 0.03, 0.12), (0, d/2-0.07, 0.06), mat((0.15, 0.1, 0.07), 0.6))
    return {"w": w, "d": d, "h": h, "window": window}


def label_texture(text_lines, size=(512, 256), bg=(235, 228, 205), fg=(30, 25, 20), fontsize=60, path=None):
    """Bild-Textur mit Text (Kalender, Schilder, Akten) via PIL."""
    from PIL import Image, ImageDraw, ImageFont
    im = Image.new("RGB", size, bg); d = ImageDraw.Draw(im)
    fp = os.path.expanduser("~/.fonts/SpecialElite.ttf")
    try: ft = ImageFont.truetype(fp, fontsize)
    except Exception: ft = ImageFont.load_default()
    y = size[1]/2 - (len(text_lines)-1)*fontsize*0.6
    for ln in text_lines:
        d.text((size[0]/2, y), ln, font=ft, fill=fg, anchor="mm"); y += fontsize*1.2
    path = path or f"/tmp/lbl_{abs(hash(tuple(text_lines)))}.png"; im.save(path)
    return path


def textured_plane(path, w, h, loc, rot, emit=0.0):
    img = bpy.data.images.load(path)
    m = bpy.data.materials.new("tex"); m.use_nodes = True; N = m.node_tree.nodes
    t = N.new("ShaderNodeTexImage"); t.image = img; b = N["Principled BSDF"]
    m.node_tree.links.new(t.outputs["Color"], b.inputs["Base Color"]); b.inputs["Roughness"].default_value = 0.8
    if emit:
        m.node_tree.links.new(t.outputs["Color"], b.inputs["Emission Color"]); b.inputs["Emission Strength"].default_value = emit
    v = [(-w/2, 0, -h/2), (w/2, 0, -h/2), (w/2, 0, h/2), (-w/2, 0, h/2)]
    o = mesh_obj("tex", v, [(0, 1, 2, 3)], m); o.location = loc; o.rotation_euler = rot
    uv = o.data.uv_layers.new()
    for i, lp in enumerate(o.data.loops): uv.data[i].uv = [(0, 0), (1, 0), (1, 1), (0, 1)][lp.vertex_index]
    return o


def desk_lamp(loc, target, energy=40, color=(1, 0.72, 0.42)):
    """Schreibtisch-/Werkbanklampe mit Schirm und warmem Spot."""
    metal = mat((0.08, 0.1, 0.08), 0.35, 0.8)
    x, y, z = loc
    cyl(0.1, 0.03, (x, y, z+0.015), metal); cyl(0.012, 0.45, (x, y, z+0.24), metal)
    shade = cyl(0.09, 0.14, (x+0.12, y, z+0.46), metal, r2=0.03, rot=(0, math.radians(-35), 0))
    bulb = sphere(0.03, (x+0.15, y, z+0.42), mat((1, 0.8, 0.5), 0.3, emit=25))
    return spot((x+0.15, y, z+0.42), target, energy=energy, color=color, size=80, blend=0.6, radius=0.03)


# ------------------------------------------------------------------ Staub / Lichtstrahl für post.py
def beam(corners_world, direction, length=4.0, strength=0.5, color=(1.0, 0.86, 0.62)):
    """Lichtstrahl, z.B. durch ein Fenster: 4 Ecken der Öffnung + Richtung des Lichts (nach innen)."""
    d = Vector(direction).normalized()
    far = [Vector(c)+d*length for c in corners_world]
    BEAMS.append({"near": [list(c) for c in corners_world], "far": [list(v) for v in far], "strength": strength, "color": color})


def dust(box_min, box_max, n=260, seed=5, drift=(0.0, 0.0, -0.004), in_beam=0):
    """Staubpartikel in einem Volumen (Welt-Koordinaten). in_beam = Index des Lichtstrahls (für Helligkeit)."""
    rnd = random.Random(seed)
    P = [[rnd.uniform(box_min[i], box_max[i]) for i in range(3)] + [rnd.random(), rnd.random()] for _ in range(n)]
    DUST.append({"pts": P, "min": list(box_min), "max": list(box_max), "drift": list(drift), "beam": in_beam})


def _cue_track(c, f0, f1):
    """Lautstärke/Stereo-Verlauf eines Geräuschs: alle 3 Frames [t, gain, pan].
    One-Shots: Verlauf ±8 s um den Anker (Länge der Datei ist hier noch unbekannt)."""
    if c["loop"]: a = max(c["f0"], f0); b = min(c["f1"], f1)
    else: a = max(f0, c["f0"]-8*SC.render.fps); b = min(f1, c["f0"]+8*SC.render.fps)
    pts = []
    for f in range(a, b+1, 3) if b > a else [a]:
        SC.frame_set(f)
        pos = c["target"].matrix_world.translation if hasattr(c["target"], "matrix_world") else Vector(c["target"])
        dist = (CAM.matrix_world.translation - pos).length
        v = world_to_camera_view(SC, CAM, pos)
        g = c["gain"] * min(1.0, c["ref"]/max(dist, 0.1))**0.9
        if v.z <= 0: g *= 0.3                                  # hinter der Kamera
        pan = max(-0.8, min(0.8, (v.x-0.5)*1.4))
        pts.append([round((f-f0)/SC.render.fps, 3), round(g, 4), round(pan, 3)])
    return {"name": c["name"], "loop": c["loop"], "track": pts, "dur": round((b-a)/SC.render.fps, 3),
            "anchor": round((c["f0"]-f0)/SC.render.fps, 3), "align": c.get("align", "start")}


def _export_meta(out, f0, f1):
    meta = {"fps": SC.render.fps, "res": [SC.render.resolution_x, SC.render.resolution_y], "frames": {}}
    meta["cues"] = [_cue_track(c, f0, f1) for c in CUES if c["f0"] <= f1]
    for f in range(f0, f1+1):
        SC.frame_set(f); fr = {"beams": [], "dust": []}
        for b in BEAMS:
            pr = lambda p: list(world_to_camera_view(SC, CAM, Vector(p)))
            fr["beams"].append({"near": [pr(p) for p in b["near"]], "far": [pr(p) for p in b["far"]], "strength": b["strength"], "color": b["color"]})
        for dd in DUST:
            pts = []
            for x, y, z, ph, sz in dd["pts"]:
                t = f - f0
                # langsames Schweben: Drift + kleine Wirbel, im Volumen umlaufend
                px = x + dd["drift"][0]*t + 0.04*math.sin(t/37+ph*20)
                py = y + dd["drift"][1]*t + 0.04*math.cos(t/43+ph*17)
                pz = z + dd["drift"][2]*t + 0.03*math.sin(t/29+ph*11)
                lo, hi = dd["min"], dd["max"]
                pz = lo[2] + (pz-lo[2]) % (hi[2]-lo[2])
                c = world_to_camera_view(SC, CAM, Vector((px, py, pz)))
                if 0 < c.z and -0.05 < c.x < 1.05 and -0.05 < c.y < 1.05: pts.append([round(c.x, 4), round(c.y, 4), round(c.z, 3), round(sz, 3), dd["beam"]])
            fr["dust"].append(pts)
        meta["frames"][f] = fr
    json.dump(meta, open(f"{out}/meta.json", "w"))


def fast_mode():
    """FAST=1: Cycles mit wenig Samples/kleiner Auflösung (≈3–4x schneller). FAST=wb: Workbench (≈10x, flacher Look)."""
    f = os.environ.get("FAST")
    if not f: return
    if f == "wb":
        SC.render.engine = "BLENDER_WORKBENCH"; sh = SC.display.shading
        sh.light = "STUDIO"; sh.color_type = "TEXTURE"; sh.show_shadows = True; sh.show_cavity = True
        sh.cavity_type = "BOTH"; SC.display.shading.shadow_intensity = 0.6
        for m in bpy.data.materials:
            try:
                b = m.node_tree.nodes.get("Principled BSDF")
                if b: m.diffuse_color = tuple(b.inputs["Base Color"].default_value)
            except Exception: pass
    else:
        SC.cycles.samples = int(os.environ.get("SAMPLES", "4")); SC.cycles.use_denoising = True
        SC.cycles.max_bounces = 2; SC.cycles.diffuse_bounces = 1; SC.cycles.glossy_bounces = 1
        SC.render.resolution_percentage = int(os.environ.get("RES_PCT", "67"))

def render(out, f0=1, f1=240, still=None):
    """Rendert PNG-Frames nach out/f_####.png und schreibt out/meta.json (Staub/Lichtstrahl)."""
    os.makedirs(out, exist_ok=True)
    fast_mode()
    SC.frame_start, SC.frame_end = f0, f1
    if os.environ.get("META_ONLY"):   # nur meta.json (Staub, Lichtstrahl, Geräusche) neu schreiben
        _export_meta(out, f0, f1); return
    if still is not None:
        SC.frame_set(still); SC.render.filepath = f"{out}/still_{still:04d}.png"
        _export_meta(out, still, still)
        bpy.ops.render.render(write_still=True); return
    _export_meta(out, f0, f1)
    SC.render.filepath = f"{out}/f_"; SC.render.image_settings.file_format = "PNG"
    bpy.ops.render.render(animation=True)
