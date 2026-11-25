"""Erzeugt bilddrehbuch.json aus scenes.json + spec.json (Satz/Teilsatz -> Bild-Ereignis)."""
import json, re
D = "/home/claude/goldsmith-pipeline/videos/005-megaspeed/"
sc = json.load(open(D+"scenes.json")); sp = json.load(open(D+"spec.json"))
KIND = {"typed":"Ort und Datum tippen","pop":"Polaroid anpinnen","words":"Roter Faden","chain":"Roter Faden","stamp":"Stempel",
        "counter":"Zahl auf Papier","quote":"Beweis-Ausdruck","doc":"Textmarker","redact":"Schwärzung","split":"Vorher/Nachher",
        "earthzoom":"Earth Zoom","dio":"Rekonstruktion im Polaroid","timeline":"Zeitstrahl am Faden","calendar":"Abreißkalender",
        "bars":"Diagramm baut sich auf","endcard":"Aktenstapel (`motion` stack)"}
MOT = {"counter":"Große Zahl (`motion` counter)","map":"Karte mit Fäden (`motion` map)","flow":"Ablauf mit Fortschrittsbalken (`motion` flow)",
       "flip":"Akte dreht sich um (`motion` flip)","grid":"Raster (`motion` grid)","cipher":"Verschlüsselung (`motion` cipher)","stack":"Aktenstapel (`motion` stack)"}
BASE = ["Foto erwacht", "Lampe schwenkt", "Polaroid anpinnen", "Foto erwacht", "Wand wächst"]
OVR = {11:"Schattenriss", 12:"Verdeckte Karte", 64:"Lupe", 63:"Lupe", 67:"Wand wächst", 69:"Foto erwacht"}
CLIPS = json.load(open(D+"clips.json")) if __import__("os").path.exists(D+"clips.json") else {}
NUM = [("nineteen sixty-three","1963"),("nineteen ninety-three","1993"),("twenty twenty-three","2023"),("twenty twenty-four","2024"),
       ("twenty twenty-five","2025"),("twenty twenty-six","2026"),("seven and a half billion dollars","7.5 billion dollars"),
       ("nine hundred billion dollars","900 billion dollars"),("thirty-three million dollars","33 million dollars"),
       ("three billion","3 billion"),("two hundred shipments","200 shipments"),("four point eight billion dollars","4.8 billion dollars"),
       ("one hundred and fifteen point eight billion dollars","115.8 billion dollars"),("thirty percent","30 percent"),("eleven days","11 days"),
       ("Four days","4 days"),("two employees","2 employees")]
NQ = {1:"frage:who",13:"antwort:who",4:"frage:spy",44:"antwort:spy",5:"frage:ceo",53:"antwort:ceo",6:"frage:pipeline",26:"antwort:pipeline",16:"frage:office",24:"antwort:office",
      29:"frage:alarms",36:"antwort:alarms",39:"frage:closed",43:"antwort:closed",50:"frage:charges",62:"antwort:charges",
      61:"frage:rules",56:"frage:fdpr",57:"antwort:fdpr",67:"frage:end",70:"antwort:end",66:"frage:testify"}
def chunks(vo):
    out = []
    for s in re.split(r"(?<=[.?!])\s+", vo):
        w = s.split()
        if len(w) <= 13: out.append(s); continue
        parts = re.split(r"(?<=,)\s+", s); cur = ""
        for p in parts:
            if cur and len((cur+" "+p).split()) > 12: out.append(cur); cur = p
            else: cur = (cur+" "+p).strip()
        if cur: out.append(cur)
    res = []
    for c in out:  # harte Grenze 14 Woerter
        w = c.split()
        while len(w) > 14: res.append(" ".join(w[:11])); w = w[11:]
        res.append(" ".join(w))
    return res
shots = []; bi = 0; kap = 0
for s in sc:
    n = s["n"]; els = sp["scenes"].get(str(n), []); used = set()
    if str(n) in sp["chapters"]:
        kap += 1
        shots.append({"satz":"", "sek":4.4, "zeigt":f"Akte rutscht über den Tisch, Deckblatt zeigt {sp['chapters'][str(n)][1]}", "animation":"Akte wird zugeschoben",
                      "inhalt":["erklaerung"], "genauigkeit":"schema", "neugier":"", "kapitel":kap})
    cs = chunks(s["vo"])
    for j, c in enumerate(cs):
        anim = None; zeigt = None
        for k, e in enumerate(els):
            if k in used: continue
            if e[1] in c:
                used.add(k)
                anim = MOT[e[2]["comp"]] if e[0] == "motion" else KIND.get(e[0], "Polaroid anpinnen")
                if e[0] == "pop" and n in OVR: anim = OVR[n]
                zeigt = f"Im Bild erscheint {anim} mit Inhalt {json.dumps(e[2], ensure_ascii=False)[:120]}"
                break
        if anim is None:
            if f"{n}:{j}" in CLIPS: anim = "Foto erwacht"; zeigt = "Echter Clip im Polaroid an der Pinnwand: " + CLIPS[f"{n}:{j}"]
            else:
                anim = OVR.get(n) or BASE[bi % len(BASE)]; bi += 1
                v = s["vis_all"][min(j, len(s["vis_all"])-1)].split(",")[0]
                zeigt = f"2,5D-Bild mit Tiefe: {v}"
        satz = c
        for a, b in NUM: satz = satz.replace(a, b)
        hard = bool(re.search(r"\d", satz)) or any(x in c.lower() for x in ("january","february","march","may","june","august","september","october","november","december"))
        inh = ["zeit"] if re.search(r"\b(19|20)\d\d\b", satz) else []
        if re.search(r"\d", satz): inh.append("zahl")
        if not inh: inh = ["geschehen"] if anim not in BASE else ["erklaerung"]
        gen = "exakt" if hard or anim in MOT.values() or anim in ("Stempel","Beweis-Ausdruck","Textmarker") else "schema"
        if anim in ("Lampe schwenkt","Wand wächst") and not hard: gen = "stimmung"; inh = ["gefuehl"]
        shots.append({"satz":satz, "zeigt":zeigt, "animation":anim, "inhalt":inh, "genauigkeit":gen,
                      "neugier": (NQ.get(n, "") if (j == 0 if NQ.get(n,"").startswith("frage") else j == len(cs)-1) else ""), "kapitel":kap, "szene":n})
json.dump(shots, open(D+"bilddrehbuch.json","w"), indent=1, ensure_ascii=False)
print(len(shots))
