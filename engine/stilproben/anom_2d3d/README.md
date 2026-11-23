# Stilprobe „Operation ANOM“ – 3D + 2D im Wechsel (22./23.11.2026)

Laurin (23.11.2026): „Der Look ist mal richtig krass! … Genau so sollte ein Video aussehen.“
Entscheidung: Diese Probe ist **zusätzliches Wissen für alle Kanäle** – sie erweitert, überschreibt aber nichts. Bisheriges bleibt (Stil, Effekte, Hook-Regeln, LESSONS.md, echte Fakten/Quellen wie Wikipedia, echte Clips, Sounds, Musik, Stimmen). Besonders gefallen haben die vielen 2D-Animationen.
Vorbild war „Die Jagd auf die Nutzer von illegalem IPTV“ (Wirklich Passiert, vidIQ-Analyse: ca. 70 % 2D / 30 % 3D, Bildwechsel alle 2–4 s).

## Aufbau (62 s, 1080p30)
| Teil | Werkzeug | Dateien |
|---|---|---|
| 3D-Szenen (Handy nachts, Serverraum, Beweismitteltisch, Schluss) | Blender per `pip install bpy`, nutzt `engine/diorama/dio.py` + `assets.py` | `3d/*.py`, `3d/render_all.sh` |
| 3D → Clip | jedes 2. Bild rendern (12 fps), `minterpolate` auf 30 fps, Lanczos auf 1080p | `ton/conv.sh` |
| 2D-Motion-Graphics + Schnitt | Remotion 4 mit System-Chrome (`--browser-executable=/usr/bin/google-chrome`), Karten mit d3-geo + world-atlas | `motion/src/*` |
| Stimme | ElevenLabs v4 Turbo (Julian), eine Datei pro Satz, Wort-Zeiten per faster-whisper | `ton/asr.py` |
| Ton-Mix | Effekte auf Bild-Ereignisse, Musik mit Ducking (−9 dB), Pausen vor großen Sätzen, Swells, Master −14 LUFS / TP −2 dB | `ton/mix.py` |

Pfade in den Skripten zeigen noch auf `/home/claude/anom/…` (Arbeitsordner der Probe) – beim Einbau in eine Kanal-Pipeline anpassen.

## Rechenzeit (2 CPU-Kerne)
- Cycles 1280×720, 8 Samples: 20–40 s pro Bild → 4 Szenen (~18 s Film) ≈ 1,5–2 h. Pro Video daher **3–4 kurze 3D-Szenen**, Rest 2D.
- Remotion-Render 62 s: ca. 12 min.

## Handwerk, das die Probe ausmacht
1. Hook in 3D mit Alltagsgegenstand (Handy geht nachts an) + eingetipptes Datum.
2. Wechsel 3D ↔ 2D-Grafik ↔ Karte, kein Bild länger als ~4 s.
3. Jede Zahl zählt hoch (Tick-Folge, bremst aus), jede Grafik kommt mit Whoosh.
4. Erklärungen als Ablauf mit **Fortschrittsbalken** oben (01 SENDEN · 02 KOPIEREN · 03 MITLESEN).
5. Neugier-Pause vor der Enthüllung (Musik weg, Herzschlag, Karte dreht sich halb), dann Flip + tiefer Treffer.
6. 3D-Szene als Bühne für 2D-Zahlen (Bilanz über dem Beweismitteltisch).
7. Schluss = offene Frage + letzter Treffer (nicht ausblenden).

## Prüfung
- earshot vs. Doku-Profil: **launch-grade, 22/23, 0 major** (nach 5 Mix-Runden: lautester Moment an der Enthüllung, Schluss-Treffer, Stereo-Breite, Mitten +3 dB bei 2 kHz).
- Gemini: „Referenz-Niveau“; „Kassenklingeln“ (price_tag) bei Bilanz-Zahlen als Stock-Klischee → durch text_click ersetzt.
