"""Poly Haven (CC0) in den Dioramen: echte Texturen, Modelle und HDRI-Licht – kostenlos, ohne Quellenpflicht.
Downloads direkt von dl.polyhaven.org (Domain muss freigegeben sein), Cache: ~/.cache/polyhaven.
Liste aller Assets: https://polyhaven.com/sitemap.xml (Slugs nach /a/). Bewährte Slugs siehe GOOD unten.

    import assets as A
    floor_mat = A.texture("wood_floor_deck", scale=1.5)       # Material mit Farbe/Normal/Rauheit
    A.model("bench_vice_01", loc=(x, y, z), rot_z=90, scale=1.0)
    A.hdri("venice_sunset", strength=0.6)                     # Umgebungslicht (optional)
"""
import os, json, math, urllib.request, ssl
import bpy

BASE = "https://dl.polyhaven.org/file/ph-assets"
CACHE = os.path.expanduser("~/.cache/polyhaven")
GOOD = {
    "textures": ["wood_floor_deck", "plastered_wall", "brick_wall_02", "asphalt_02", "clean_asphalt", "brushed_concrete",
                 "clay_roof_tiles_02", "cobblestone_01", "brick_pavement", "chipped_concrete", "blue_plaster_weathered"],
    "models": ["bench_vice_01", "desk_lamp_arm_01", "mantel_clock_01", "alarm_clock_01", "Shelf_01", "WoodenChair_01",
               "WoodenTable_01", "wooden_crate_01", "cardboard_box_01", "wooden_stool_01", "vintage_cabinet_01",
               "street_lamp_01", "street_lamp_02", "utility_box_01", "potted_plant_01", "Television_01",
               "book_encyclopedia_set_01", "vintage_grandfather_clock_01", "Lantern_01", "wooden_barrels_01"],
    "hdris": ["venice_sunset", "cobblestone_street_night", "dresden_station_night", "alps_field"],
}


def _get(url, path):
    if os.path.exists(path) and os.path.getsize(path) > 0: return path
    os.makedirs(os.path.dirname(path), exist_ok=True)
    ctx = ssl.create_default_context(cafile=os.environ.get("SSL_CERT_FILE") or None)
    with urllib.request.urlopen(url, timeout=120, context=ctx) as r, open(path + ".part", "wb") as f: f.write(r.read())
    os.replace(path + ".part", path); return path


# ------------------------------------------------------------------ Texturen
def texture(slug, scale=1.0, res="1k", tint=None, rough_mul=1.0, bump=1.0):
    """Material aus einer Poly-Haven-Textur. Box-Projektion über Objektkoordinaten (keine UVs nötig).
    scale = Wiederholungen pro Meter. tint = (r,g,b) Multiplikator für die Farbe (z.B. dunkler/wärmer)."""
    key = f"ph_{slug}_{scale}_{tint}"
    if key in bpy.data.materials: return bpy.data.materials[key]
    d = f"{CACHE}/tex/{slug}"; maps = {}
    for kind in ("diff", "nor_gl", "rough"):
        p = f"{d}/{slug}_{kind}_{res}.jpg"
        try: maps[kind] = _get(f"{BASE}/Textures/jpg/{res}/{slug}/{slug}_{kind}_{res}.jpg", p)
        except Exception as e: print("Textur fehlt:", slug, kind, e)
    m = bpy.data.materials.new(key); m.use_nodes = True; nt = m.node_tree; N = nt.nodes; L = nt.links
    b = N["Principled BSDF"]
    tc = N.new("ShaderNodeTexCoord"); mp = N.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (scale, scale, scale)
    L.new(tc.outputs["Object"], mp.inputs["Vector"])
    def img(kind, non_color=False):
        if kind not in maps: return None
        t = N.new("ShaderNodeTexImage"); t.image = bpy.data.images.load(maps[kind], check_existing=True)
        t.projection = "BOX"; t.projection_blend = 0.25
        if non_color: t.image.colorspace_settings.name = "Non-Color"
        L.new(mp.outputs["Vector"], t.inputs["Vector"]); return t
    c = img("diff")
    if c:
        if tint:
            mx = N.new("ShaderNodeMix"); mx.data_type = "RGBA"; mx.blend_type = "MULTIPLY"; mx.inputs["Factor"].default_value = 1.0
            L.new(c.outputs["Color"], mx.inputs["A"]); mx.inputs["B"].default_value = (*tint, 1)
            L.new(mx.outputs["Result"], b.inputs["Base Color"])
        else: L.new(c.outputs["Color"], b.inputs["Base Color"])
    r = img("rough", True)
    if r:
        if rough_mul != 1.0:
            mm = N.new("ShaderNodeMath"); mm.operation = "MULTIPLY"; mm.inputs[1].default_value = rough_mul
            L.new(r.outputs["Color"], mm.inputs[0]); L.new(mm.outputs[0], b.inputs["Roughness"])
        else: L.new(r.outputs["Color"], b.inputs["Roughness"])
    n = img("nor_gl", True)
    if n:
        nm = N.new("ShaderNodeNormalMap"); nm.inputs["Strength"].default_value = bump
        L.new(n.outputs["Color"], nm.inputs["Color"]); L.new(nm.outputs["Normal"], b.inputs["Normal"])
    return m


# ------------------------------------------------------------------ Modelle (glTF)
def _fetch_gltf(slug, res):
    d = f"{CACHE}/mdl/{slug}_{res}"; g = f"{d}/{slug}_{res}.gltf"
    _get(f"{BASE}/Models/gltf/{res}/{slug}/{slug}_{res}.gltf", g)
    j = json.load(open(g))
    for item in j.get("buffers", []) + j.get("images", []):
        u = item.get("uri")
        if u and not u.startswith("data:"):
            try: _get(f"{BASE}/Models/gltf/{res}/{slug}/{u}", f"{d}/{u}")
            except Exception:   # Modell-Texturen liegen separat unter Models/jpg
                _get(f"{BASE}/Models/jpg/{res}/{slug}/{os.path.basename(u)}", f"{d}/{u}")
    return g


_LOADED = {}
def model(slug, loc=(0, 0, 0), rot_z=0.0, scale=1.0, res="1k", rot=None):
    """Poly-Haven-Modell einfügen (echte Maße in Metern). Gibt ein Wurzel-Empty zurück (animierbar).
    Mehrfach verwendet -> Meshes werden geteilt (schnell)."""
    import dio as D
    if slug not in _LOADED:
        g = _fetch_gltf(slug, res)
        before = set(bpy.data.objects)
        bpy.ops.import_scene.gltf(filepath=g)
        new = [o for o in bpy.data.objects if o not in before]
        widgets = {pb.custom_shape for o in new if o.type == "ARMATURE" for pb in o.pose.bones if pb.custom_shape}
        new = [o for o in new if o not in widgets and not o.name.startswith(("Icosphere", "WGT"))]   # Bone-Formen nicht rendern
        for o in new:
            for c in o.users_collection: c.objects.unlink(o)
        _LOADED[slug] = new
    src = _LOADED[slug]
    root = D.empty(loc, f"ph_{slug}"); root.rotation_euler = rot or (0, 0, math.radians(rot_z)); root.scale = (scale,)*3
    mp = {}
    for o in src:
        c = o.copy(); mp[o] = c; D.SC.collection.objects.link(c)
    for o, c in mp.items():
        c.parent = mp.get(o.parent, root) if o.parent in mp else root
        if o.parent not in mp: c.matrix_parent_inverse.identity()
    return root


# ------------------------------------------------------------------ HDRI
def hdri(slug, strength=1.0, res="1k", rotation=0.0, camera_visible=True):
    p = _get(f"{BASE}/HDRIs/hdr/{res}/{slug}_{res}.hdr", f"{CACHE}/hdri/{slug}_{res}.hdr")
    w = bpy.context.scene.world; nt = w.node_tree; N = nt.nodes; L = nt.links
    env = N.new("ShaderNodeTexEnvironment"); env.image = bpy.data.images.load(p, check_existing=True)
    mp = N.new("ShaderNodeMapping"); tc = N.new("ShaderNodeTexCoord"); mp.inputs["Rotation"].default_value[2] = math.radians(rotation)
    L.new(tc.outputs["Generated"], mp.inputs["Vector"]); L.new(mp.outputs["Vector"], env.inputs["Vector"])
    bg = N["Background"]; L.new(env.outputs["Color"], bg.inputs["Color"]); bg.inputs["Strength"].default_value = strength
    return env
