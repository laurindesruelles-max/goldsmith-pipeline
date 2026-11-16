"""Endkontrolle (Technik) für ein fertiges Video + Vorlage für den Prüfbericht.

usage: python3 engine/qa.py <video.mp4> <videos/NNN-slug> [--min 480] [--lufs -14]
Schreibt <videos/NNN-slug>/qa.md (Technik-Teil automatisch, Inhalt/Recht/Lizenzen als Checkliste zum Ausfüllen)
und <videos/NNN-slug>/qa_frames.jpg (Kontaktbogen: 1 Bild alle ~30 s zum Ansehen auf Tippfehler/Fehler).
Exit-Code 1, wenn ein Technik-Punkt durchfällt (dann NICHT hochladen, erst beheben).
"""
import sys, os, re, json, subprocess, argparse
from datetime import date


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def probe(v):
    j = json.loads(run(["ffprobe", "-v", "error", "-show_entries", "format=duration,size:stream=codec_type,width,height,r_frame_rate",
                        "-of", "json", v]).stdout)
    return j


def loudness(v):
    out = run(["ffmpeg", "-nostats", "-i", v, "-vn", "-af", "ebur128=peak=true", "-f", "null", "-"]).stderr
    I = re.findall(r"I:\s+(-?[\d.]+) LUFS", out); TP = re.findall(r"Peak:\s+(-?[\d.]+) dBFS", out)
    return (float(I[-1]) if I else None), (float(TP[-1]) if TP else None)


def detect(v, flt, key):
    out = run(["ffmpeg", "-nostats", "-i", v, "-vf", flt, "-an", "-f", "null", "-"]).stderr
    return re.findall(key, out)


def contact(v, dur, out, every=30):
    n = max(6, int(dur // every)); cols = 4; rows = (n + cols - 1)//cols
    ts = [dur*(i+0.5)/n for i in range(n)]; tmp = "/tmp/qa_frames"; os.makedirs(tmp, exist_ok=True)
    for i, t in enumerate(ts):
        run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{t:.2f}", "-i", v, "-frames:v", "1", "-vf",
             f"scale=480:-1,drawtext=text='{int(t//60)}\\:{int(t%60):02d}':x=8:y=8:fontsize=22:fontcolor=white:box=1:boxcolor=black@0.6", f"{tmp}/{i:03d}.jpg"])
    run(["ffmpeg", "-y", "-loglevel", "error", "-i", f"{tmp}/%03d.jpg", "-vf", f"tile={cols}x{rows}", "-frames:v", "1", out])
    for f in os.listdir(tmp): os.remove(f"{tmp}/{f}")


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("video"); ap.add_argument("vdir")
    ap.add_argument("--min", type=float, default=480); ap.add_argument("--lufs", type=float, default=-14); a = ap.parse_args()
    p = probe(a.video); dur = float(p["format"]["duration"]); size = int(p["format"]["size"])/1e6
    vs = [s for s in p["streams"] if s["codec_type"] == "video"]; aus = [s for s in p["streams"] if s["codec_type"] == "audio"]
    I, TP = loudness(a.video)
    black = detect(a.video, "blackdetect=d=0.8:pix_th=0.06", r"black_start:([\d.]+)")
    freeze = detect(a.video, "freezedetect=n=0.002:d=4", r"freeze_start: ([\d.]+)")
    res = []
    def chk(ok, txt): res.append(("OK" if ok else "FEHLER", txt)); return ok
    chk(dur >= a.min, f"Länge {int(dur//60)}:{int(dur%60):02d} (Minimum {int(a.min//60)}:{int(a.min%60):02d})")
    chk(bool(vs) and vs[0].get("width") == 1920 and vs[0].get("height") == 1080, f"Bild {vs[0].get('width')}x{vs[0].get('height')}" if vs else "kein Bild")
    chk(bool(aus), "Tonspur vorhanden")
    chk(I is not None and abs(I - a.lufs) <= 2.5, f"Lautheit {I} LUFS (Ziel {a.lufs} ±2,5)")
    chk(TP is not None and TP <= -0.5, f"Spitzenpegel {TP} dBFS (max. −0,5)")
    chk(not [b for b in black if 1.0 < float(b) < dur-3], f"Schwarzbilder mitten im Video: {', '.join(b for b in black if 1.0 < float(b) < dur-3) or 'keine'}")
    chk(len(freeze) <= 3, f"Standbild-Stellen (≥4 s ohne Bewegung): {len(freeze)} {('bei ' + ', '.join(f[:6] for f in freeze[:6]) + ' s') if freeze else ''}")
    res.append(("OK", f"Dateigröße {size:.0f} MB (Info – Upload-Kopie muss < 299 MB sein)"))
    os.makedirs(a.vdir, exist_ok=True); contact(a.video, dur, f"{a.vdir}/qa_frames.jpg")
    failed = [r for r in res if r[0] != "OK"]
    md = [f"# Prüfbericht – {os.path.basename(a.vdir)} ({date.today().isoformat()})", "",
          "## 1. Technik (automatisch, engine/qa.py)"] + [f"- [{'x' if s == 'OK' else ' '}] {s}: {t}" for s, t in res] + [
          "- [ ] Kontaktbogen `qa_frames.jpg` angesehen: Tippfehler in Einblendungen, abgeschnittener Text, Bildfehler, Ton synchron (Stichproben)",
          "", "## 2. Fakten (unabhängiger Faktencheck durch separaten Agenten)",
          "Tabelle: Aussage im Skript | Quelle (Link) | Stimmt? (ja / teilweise / nein / unbelegt) | Korrektur",
          "- [ ] Jede Zahl, jedes Datum, jeder Name, jedes Zitat geprüft; alles mit „nein“/„unbelegt“ wurde geändert oder gestrichen",
          "", "## 3. Recht (keine Rechtsberatung – Sorgfaltsprüfung)",
          "- [ ] Äußerungsrecht: Tatsachen nur mit Beleg; Vorwürfe/laufende Verfahren als „Vorwurf“/„laut …“; Urteile korrekt (Gericht, Jahr); Meinung als Meinung erkennbar; keine Beleidigung, keine Spekulation über Privates",
          "- [ ] Personen: keine echten Fotos, keine realistischen KI-Gesichter realer Personen, keine Privatpersonen identifizierbar",
          "- [ ] Marken: keine Logos/Markenzeichen im Bild oder Thumbnail; Markennamen nur beschreibend; Hinweis „not affiliated/endorsed“ in der Beschreibung",
          "- [ ] Titel und Thumbnail versprechen nichts, was das Video nicht belegt (kein irreführender Vorwurf)",
          "", "## 4. Lizenzen (Protokoll)",
          "| Material | Quelle | Lizenz |", "|---|---|---|",
          "| Sprecherstimme | Higgsfield (Preset-Stimme) | Higgsfield-Abo (kommerzielle Nutzung laut Plan) |",
          "| KI-Bilder / Thumbnail | Higgsfield gpt_image | Higgsfield-Abo |",
          "| Musik | assets/music (ElevenLabs über Higgsfield) | Higgsfield-Abo |",
          "| Geräusche | assets/sfx (SOUNDS.md) – SFXMint | CC0 |",
          "| 3D-Texturen/Modelle | Poly Haven | CC0 |",
          "| Schriften | Anton, Special Elite, Playfair Display, Inter | SIL OFL / Apache |",
          "- [ ] Kein fremdes Material (Filmausschnitte, Fotos, Musik) außer den oben gelisteten Quellen",
          "", "## 5. YouTube",
          "- [ ] Realistisch wirkende KI-Bilder echter Orte/Ereignisse → beim Upload „Veränderte oder synthetische Inhalte: Ja“ setzen (Laurin im Studio, falls die API es nicht kann)",
          "- [ ] Beschreibung: Quellenliste, Kapitel, Marken-Hinweis; keine < oder > Zeichen",
          "- [ ] Werbefreundlich: keine Gewaltbilder, keine Schimpfwörter, keine reißerischen Schock-Thumbnails mit Verletzungen",
          "", f"## Ergebnis: {'TECHNIK OK' if not failed else 'TECHNIK FEHLER – NICHT HOCHLADEN'} · Fakten/Recht/Lizenzen: oben abhaken, erst dann Laurin zur Freigabe schicken"]
    open(f"{a.vdir}/qa.md", "w").write("\n".join(md) + "\n")
    for s, t in res: print(s, "-", t)
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
