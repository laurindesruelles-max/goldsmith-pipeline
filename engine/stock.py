"""Kostenloses echtes Videomaterial von Pixabay (Pixabay Content License: kommerziell ok, keine Namensnennung nötig;
NICHT erlaubt: Clips mit erkennbaren Marken/Logos für Waren/Dienstleistungen, unbearbeitet weiterverkaufen).
Schlüssel NUR zur Laufzeit: export PIXABAY_KEY=... (steht im Video-Skill und im geplanten Lauf; nie ins Repo schreiben – Repo ist öffentlich).

python3 engine/stock.py search "city traffic night" [n]      -> Liste: id | Dauer | Tags | Größe
python3 engine/stock.py get <id> <ziel.mp4>                     -> lädt 'large' (1080p+) bzw. 'medium', ohne Ton, 24 fps
Regeln (Goldsmith): keine Logos/Marken im Bild, keine erkennbaren Gesichter in negativem Zusammenhang, immer bearbeiten
(Grade, Grain, Zuschnitt), Ton wird verworfen. Ablage: work/vid/<key>.mp4 (part2.py nutzt den Clip automatisch statt des Standbilds).
Lizenz-Zeile in qa.md: "Pixabay-Video <id> – Pixabay Content License".
"""
import os, sys, json, subprocess, urllib.request, urllib.parse

UA = {"User-Agent": "GoldsmithProductions/1.0 (stock footage tool)"}
def _open(u): return urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=60)

def _key():
    k = os.environ.get("PIXABAY_KEY")
    if not k: sys.exit("PIXABAY_KEY fehlt – Laurin nach dem Schlüssel fragen")
    return k

def search(q, n=10):
    u = "https://pixabay.com/api/videos/?" + urllib.parse.urlencode({"key": _key(), "q": q, "per_page": max(3, n), "safesearch": "true"})
    d = json.load(_open(u))
    return [(h["id"], h["duration"], h["tags"], h["videos"]["large"]["width"] or h["videos"]["medium"]["width"]) for h in d["hits"][:n]]

def get(vid, out):
    u = "https://pixabay.com/api/videos/?" + urllib.parse.urlencode({"key": _key(), "id": vid})
    h = json.load(_open(u))["hits"][0]["videos"]
    src = (h["large"]["url"] or h["medium"]["url"])
    tmp = out + ".dl.mp4"; open(tmp, "wb").write(_open(src).read())
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", tmp, "-an", "-vf", "scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,fps=24",
                    "-c:v", "libx264", "-crf", "18", "-preset", "veryfast", out], check=True)
    os.remove(tmp)

if __name__ == "__main__":
    if sys.argv[1] == "search":
        for r in search(sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 10): print(*r, sep=" | ")
    elif sys.argv[1] == "get":
        get(sys.argv[2], sys.argv[3]); print("ok", sys.argv[3])
