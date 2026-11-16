"""Vorlage: Earth-Zoom-Abstieg – Stadt auf Hügeln (Beispiel GTA 6: Edinburgh, Abend; per Env anpassbar).
Abgeleitet von aerial_town.py (Bergtal mit Kleinstadt, Kamera sinkt von hoch oben bis vor ein Fenster.
(Beispiel Luxottica: Agordo in den Dolomiten, Abend, Werkstattfenster leuchtet.)
usage: python3 aerial_town.py <outdir> [still_frame]
Anpassen pro Video: Gelände (terrain flach/bergig), Stadtgröße, Zielhaus, Tageszeit, Länge.
Der erste Frame ist (fast) eine Draufsicht – daran schließt der 2D-Kartenzoom (effects.earthzoom) an,
der letzte Frame zeigt das leuchtende Fenster bildfüllend – daraus blendet die Innenraum-Szene auf.
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import dio as D

OUT = sys.argv[1]; STILL = int(sys.argv[2]) if len(sys.argv) > 2 else None
F1 = int(os.environ.get("F1", "150"))
D.reset(samples=int(os.environ.get("SAMPLES", "8")), world=(0.22, 0.27, 0.42), world_strength=0.45)

D.terrain(size=1700, res=170, valley=150, peak=110, seed=9, snow=2.0, river=False)
houses = D.town(center=(0, 0), n=150, spread=110, seed=21, lit=0.55)
for h in houses:
    for c in h.children:
        if c.name.startswith("roof") and c.data.materials: c.data.materials[0] = D.mat((0.16, 0.17, 0.19), 0.7)   # Schieferdächer
# Zielhaus (Werkstatt) mit großem, warm leuchtendem Fenster zur Kamera (-y)
hx, hy = D.valley_x(-10) + 22, -10
for h in list(houses):
    if math.hypot(h.location.x-hx, h.location.y-hy) < 14:
        for c in list(h.children): D.bpy.data.objects.remove(c, do_unlink=True)
        D.bpy.data.objects.remove(h, do_unlink=True); houses.remove(h)
for o in list(D.bpy.data.objects):   # Bäume direkt vor dem Zielhaus entfernen (verdecken das Fenster)
    if o.type == "MESH" and o.parent is None and math.hypot(o.location.x-hx, o.location.y-(hy-8)) < 11 and o.location.z < 12:
        D.bpy.data.objects.remove(o, do_unlink=True)
tgt = D.house((hx, hy, 0), 12, 6, 9.5, rot=0, wall=(0.55, 0.5, 0.43), roof=(0.16, 0.17, 0.19), lit=0.5, seed=99, flat=True)
win = D.box((1.6, 0.08, 1.5), (hx-1.2, hy-3.03, 3.0), D.mat((1.0, 0.68, 0.36), 0.4, emit=9.0))
D.box((1.75, 0.1, 0.07), (hx-1.2, hy-3.05, 3.0), D.mat((0.15, 0.1, 0.07), 0.6)); D.box((0.07, 0.1, 1.6), (hx-1.2, hy-3.05, 3.0), D.mat((0.15, 0.1, 0.07), 0.6))
D.box((1.6, 0.08, 1.4), (hx+1.6, hy-3.03, 3.0), D.mat((0.05, 0.05, 0.06), 0.3))
D.point((hx-1.2, hy-2.0, 3.0), energy=200, color=(1, 0.7, 0.4), radius=0.5)
# kleines Schild über der Tür
D.box((3.2, 0.1, 0.5), (hx+1.5, hy-3.06, 6.0), D.mat((0.12, 0.12, 0.13), 0.6))
# Autos auf der Talstraße (eins fährt)
c1 = D.car((D.valley_x(-60)-14, -60, 0.2), rot=math.pi/2, color=(0.5, 0.12, 0.08), lights=True, length=4.4)
D.drive(c1, 1, F1, (D.valley_x(-80)-14.8, -80, 0.2), (D.valley_x(5)-14.8, 5, 0.2))
D.car((D.valley_x(-14)-13.2, -14, 0.2), rot=-math.pi/2, color=(0.2, 0.25, 0.32), length=4.4)
# Figur auf dem Weg zum Haus
J = D.figure((hx-6, hy-9, 0.2), rot=math.radians(30), shirt=(0.3, 0.25, 0.2), coat=True, hat=True, seed=5)
D.walk(J, 1, F1, (hx-9, hy-12, 0.2), (hx-2, hy-6, 0.2))

# Abendsonne, tief und warm
s = D.sun(rot=(math.radians(72), 0, math.radians(-35)), energy=2.4, color=(1.0, 0.55, 0.32), angle=3)
# Kamera: Draufsicht hoch oben -> Sinkflug -> vor das Fenster
D.camera(lens=35)
wx, wy, wz = hx-1.2, hy-3.03, 3.0
D.camera_path([
    (1,        (hx+5, hy-40, 900),  (hx, hy, 0), 35),
    (int(F1*0.45), (hx+25, hy-130, 170), (hx, hy, 2), 35),
    (int(F1*0.78), (wx+6, wy-38, 16), (wx, wy, 3.5), 40),
    (F1,       (wx, wy-2.1, 3.0),   (wx, wy+5, 3.0), 40),
])
D.render(OUT, 1, F1, still=STILL)
