"""2D-Motion-Graphics fuer Goldsmith (spec-Kind "motion"), gebaut mit Remotion (engine/motion/).
Erweiterung aus der Stilprobe "Operation ANOM" (Laurin 23.11.2026: "Genau so sollte ein Video aussehen", vor allem die
vielen 2D-Animationen). Ersetzt keine bestehenden Effekte (doc, redact, chart, route, news, photo, dio ...), sondern
ergaenzt sie – im Goldsmith-Look: dunkler Ermittlertisch, Elfenbein-Papier, rote Faeden, Gold, Anton + Schreibmaschine.

spec.json:  ["motion", anchor, {"comp": "<baustein>", "props": {...}, "dur": 5.0 | "scene"}]

Bausteine (props -> engine/motion/src/comps.tsx):
  map     Karte mit Stecknadeln + roten Faeden, optional Punkte-Schwarm, Laender rot, Zaehler.
          {"label": "THE SUPPLY CHAIN", "title": "ONE COMPANY", "view": "world"|"europe"|[lon, lat, scale],
           "pins": [{"lonlat": [12.03, 46.27], "label": "AGORDO, ITALY"}, {"id": "840", "label": "USA"}],
           "threads": "chain"|"none"|[[0, 2], [1, 2]], "swarm": 120, "highlight": ["276", "380"],
           "counter": {"value": 100, "suffix": "+", "label": "COUNTRIES"}, "pulse": true}
          (id = ISO-3166 numerisch, z. B. 276 Deutschland, 840 USA, 380 Italien)
  flow    Ablauf mit Fortschrittsbalken; Paket wandert von Station zu Station, optional Abzweig nach unten.
          {"label": "HOW THE MONEY MOVED", "steps": ["Payment", "Diverted", "Hidden"], "packet": "money"|"envelope"|"doc",
           "nodes": [{"label": "CUSTOMER", "icon": "person"}, ...], "branch": {"after": 1, "label": "SHELL FIRM", "icon": "doc", "text": "SKIMMED"}}
          Icons: phone server bank factory person ship money doc store lock eye gavel
  flip    Akte dreht sich um -> Enthuellung (Neugier-Pause davor!). {"teaser": "But who really owned it ...",
           "front": {"title": "RAY-BAN", "icon": "eye"}, "back": {"title": "LUXOTTICA", "sub": "OWNER SINCE 1999"}, "at": 2.4}
  counter Grosse Zahl zaehlt hoch, dahinter fliegen Geldscheine/Nachrichten/Akten.
          {"label": "ANNUAL REVENUE", "value": 25.4, "dec": 1, "prefix": "€", "suffix": " BN", "caption": "PER YEAR", "items": "money"|"messages"|"docs"|"none"}
  grid    Viele Kaertchen fuellen sich + Zahl. {"label": "...", "icon": "store", "value": 9000, "suffix": "+", "caption": "STORES WORLDWIDE", "n": 60, "hot": 9}
  phone   Handy mit Chat + getipptem Zitat. {"label": "LEAKED CHAT", "app": "MESSAGES", "messages": [["text", false], ["antwort", true]], "quote": "..."}
          Nur echte, belegte Zitate als quote; sonst Nachrichten klar als Nachstellung kennzeichnen (label "RECONSTRUCTION").
  cipher  Text verschluesselt sich. {"label": "ENCRYPTED", "text": "TRANSFER 4.2M TO ZURICH", "caption": "UNREADABLE TO OUTSIDERS"}
  stack   Verfahren/Akten stapeln sich, Symbol knallt drauf, Frage tippt. {"label": "STILL IN COURT", "cards": [["CASE 1", "Antitrust · EU"], ...], "symbol": "?"|"§", "question": "..."}

Fakten in props muessen belegt sein (Quellen im Skript) – wie bei doc/news/chart. Faustregel aus der ANOM-Probe:
ca. alle 2–4 s ein neues Bild; motion-Clips 3–6 s; 6–12 motion-Clips pro Video zusaetzlich zu den bisherigen Effekten.

Ablauf: nach "part2.py meta" (Timing steht) einmal  `python3 <repo>/engine/motion_fx.py build`  im Arbeitsordner v3/
-> rendert alle motion-Clips aus spec.json nach v3/motion/<key>.mp4 (Remotion, ~10 s Rechenzeit pro Sekunde Clip auf 2 Kernen;
nicht parallel zu Blender laufen lassen). Einmalig: `cd <repo>/engine/motion && npm install`.
Ist der Clip kuerzer als die Szene ("dur": "scene"), haelt er das letzte Bild. Sounds kommen automatisch (motion_sounds).
"""
import os, sys, json, hashlib, subprocess
import numpy as np, cv2
from PIL import Image

W, H = 1920, 1080
HERE = os.path.dirname(os.path.abspath(__file__))
MOTION = os.path.join(HERE, "motion")
FPS = 30
DEFAULT_LEN = {"map": 5.0, "flow": 5.5, "flip": 4.0, "counter": 4.0, "grid": 4.5, "phone": 4.5, "cipher": 3.0, "stack": 4.5}


def clip_len(p, dur=None):
    """Laenge des gerenderten Clips: params["len"] oder Szenen-Dauer (max 7 s) oder Standard."""
    if p.get("len"): return float(p["len"])
    base = DEFAULT_LEN.get(p["comp"], 5.0)
    if dur: return round(min(max(base, dur), 7.0), 2)
    return base


def key_of(p):
    j = json.dumps({"c": p["comp"], "p": p.get("props", {}), "l": p.get("len")}, sort_keys=True, ensure_ascii=False)
    return hashlib.sha1(j.encode()).hexdigest()[:12]


_CAP = {}
def _frame(path, idx):
    cap = _CAP.get(path)
    if cap is None:
        if len(_CAP) > 3:
            for c in _CAP.values(): c[0].release()
            _CAP.clear()
        cap = [cv2.VideoCapture(path), -1, None, int(cv2.VideoCapture(path).get(cv2.CAP_PROP_FRAME_COUNT))]; _CAP[path] = cap
    idx = max(0, min(idx, cap[3]-1))
    if idx == cap[1]: return cap[2]
    if idx != cap[1]+1: cap[0].set(cv2.CAP_PROP_POS_FRAMES, idx)
    ok, fr = cap[0].read()
    if not ok: return cap[2]
    fr = cv2.cvtColor(fr, cv2.COLOR_BGR2RGB)
    if fr.shape[1] != W: fr = cv2.resize(fr, (W, H), interpolation=cv2.INTER_LANCZOS4)
    cap[1], cap[2] = idx, fr
    return fr


def motion(t, T, p, ctx):
    path = f"motion/{key_of(p)}.mp4"
    if not os.path.exists(path):
        print("motion-Clip fehlt (erst motion_fx.py build):", path); return None
    fr = _frame(path, int(t*FPS))
    return fr.copy(), Image.new("RGBA", (W, H), (0, 0, 0, 0))


# ---------- Sounds: gleiche Zeitpunkte wie in comps.tsx (MAP_T, FLOW_T ...) ----------
CPS = 18
def _keys(t0, text, g=0.4):
    return [(t0+k/CPS, f"key{k % 8}", g) for k, ch in enumerate(text) if ch != " " and k % 2 == 0]
def _ticks(t0, dur, n=10, g=0.3):
    return [(t0+dur*(1-(1-i/(n-1))**2.2), "tick", g*(1-0.6*i/(n-1))) for i in range(n)]


def motion_sounds(p, dur):
    c, q = p["comp"], p.get("props", {})
    ev = [(0.0, "diagram_whoosh", 0.3)]
    if q.get("label"): ev += [(0.15, "paper_slide", 0.3)]
    if c == "map":
        if q.get("swarm"): ev += [(0.2+i*0.2, "pin_pop", 0.18) for i in range(7)]
        for i, pn in enumerate(q.get("pins", [])):
            t = 0.45+i*0.55; ev += [(t, "pin_pop", 0.7)]
            if i > 0 and q.get("threads", "chain") != "none": ev += [(t-0.35, "zip", 0.35)]
            if pn.get("label"): ev += _keys(t+0.15, pn["label"], 0.35)
        if q.get("highlight"): ev += [(0.3, "data_loading", 0.35)]
        if q.get("counter"): ev += _ticks(0.4, 1.2, 10, 0.2) + [(1.6, "text_click", 0.5)]
        if q.get("title"): ev += [(0.15, "text_click", 0.5)]
    elif c == "flow":
        n = len(q.get("nodes", []))
        ev += [(0.1+i*0.15, "pin_pop", 0.4) for i in range(n)]
        ev += [(0.6+0.75*i, "whoosh", 0.25) for i in range(max(0, n-1))]
        b = q.get("branch")
        if b:
            bt = 0.6+0.75*(b["after"]+0.5)
            ev += [(bt, "glitch", 0.35), (bt+0.5, "pin_pop", 0.6), (bt+0.7, "sub_drop", 0.7), (bt+0.72, "text_click", 0.5)]
    elif c == "flip":
        at = q.get("at", 2.4)
        if q.get("teaser"): ev += _keys(0.25, q["teaser"], 0.3)
        ev += [(0.2, "heartbeat", 0.45), (at-0.6, "glitch", 0.55), (at-0.05, "whoosh", 0.6), (at+0.12, "sub_drop", 1.2), (at+0.14, "zoom_deep_impact", 0.5)]
    elif c == "counter":
        ev += _ticks(0.1, 1.6, 12, 0.18) + [(0.9, "text_click", 0.5)]
        if q.get("items") == "money": ev += [(0.3, "coins", 0.35)]
    elif c == "grid":
        ev += [(0.2, "paper_slide", 0.25), (0.65, "paper_slide", 0.2), (1.1, "paper_slide", 0.18)] + _ticks(0.9, 1.0, 10, 0.2) + [(1.6, "text_click", 0.5)]
    elif c == "phone":
        for i in range(len(q.get("messages", []))): ev += [(0.15+i*0.4, "phone_notify" if i == 0 else "pin_pop", 0.4)]
        if q.get("quote"): ev += _keys(0.15+len(q["messages"])*0.4, q["quote"], 0.35)
    elif c == "cipher":
        ev += [(0.3, "glitch", 0.4), (0.35, "data_loading", 0.4), (0.9, "text_click", 0.5)]
    elif c == "stack":
        ev += [(0.1+i*0.16, "paper_slide", 0.35) for i in range(len(q.get("cards", [])))]
        ev += [(1.5, "stamp", 0.8), (1.52, "sub_drop", 0.5)]
        if q.get("question"): ev += _keys(0.6, q["question"], 0.3)
    return [e for e in ev if e[0] < dur]


# ---------- Build: alle motion-Clips aus spec.json rendern ----------
def build(spec="spec.json"):
    sp = json.load(open(spec)); jobs = []
    timing = json.load(open("timing.json")) if os.path.exists("timing.json") else {}
    os.makedirs("motion", exist_ok=True)
    for n, ov in sp.get("scenes", {}).items():
        for o in ov:
            if o[0] != "motion": continue
            p = o[2]; out = os.path.abspath(f"motion/{key_of(p)}.mp4")
            if os.path.exists(out): continue
            d = p.get("dur"); d = float(d) if isinstance(d, (int, float)) else None
            jobs.append({"comp": p["comp"], "props": p.get("props", {}), "len": clip_len(p, d), "out": out})
    if not jobs: print("keine neuen motion-Clips"); return
    jf = os.path.abspath("motion/jobs.json"); json.dump(jobs, open(jf, "w"), ensure_ascii=False, indent=1)
    print(f"{len(jobs)} motion-Clips rendern ...")
    subprocess.run(["node", os.path.join(MOTION, "render.mjs"), jf], check=True)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "build": build(*(sys.argv[2:3]))
    else: print(__doc__)
