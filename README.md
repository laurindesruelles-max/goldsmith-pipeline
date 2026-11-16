# Goldsmith Productions – Video-Pipeline

Faceless-Doku-Kanal @goldsmith-productions („The stories behind the brands you know“).
Stil: „Ermittlungsakte“ – realistische Bilder, Pinnwand, Polaroids, rote Fäden, Schreibmaschinentext
mit mechanischem Tastatursound, Stempel, hochzählende Zahlen, Kapitelkarten, Filmkorn, Spannungsmusik.

## Ablauf pro Video
1. **Thema** wählen (vidIQ-Ausreißer / News-Radar). Wirtschaftskrimi hinter einer bekannten Marke oder aktuelles Wirtschaftsthema.
2. **Skript**: 50–60 Szenen, ~10 Min, Englisch. `videos/NNN-slug/scenes.json` mit `n`, `vo`, `vis`. Quellen prüfen. → Freigabe durch Laurin.
3. **Stimme**: Higgsfield `seed_audio`, Preset-Stimme Alistair `d9d5c263-f84e-4752-97b5-3750fcc6fd2f`, eine WAV pro Szene → `audio/N.wav` (max. 6 Jobs parallel).
4. **Bilder**: Higgsfield `gpt_image_2_6`, 16:9, dunkler Ermittlungs-Look (warmes Lampenlicht, Pinnwand, Akten), eine pro Szene → `img/N.png`. Keine echten Logos, keine echten Personenfotos.
5. **Timing**: Sprechpausen per ffmpeg `silencedetect` → `timing.json`.
6. **Overlay-Spec**: zusätzlich in spec.json `"music": {"1":"music_tension","7":"emotional_piano",...}` (Track ab Szene N, siehe LESSONS.md) und `"beats": {"3": [["It isn't.", 1.2]]}` (Spannungspause nach dem Satz mit diesem Text, Musik taucht ab, Braam/Boom automatisch). Vollbild-Effekte (engine/effects.py, Doku im Dateikopf): doc, redact, chart, route, split, news, parallax – als spec-Kinds mit Parameter-Objekt. Für parallax vorher Higgsfield remove_background aufs Szenenbild → img/N_fg.png. Danach:  pro Szene (siehe `S`-Dict in `engine/part2.py`): `typed` (Jahr/Ort), `pop` (Schlagwort), `stamp`, `counter` (Zahl), `chain`, `quote`, `brands`, `words`, `map`. Kapitelstarts in `CH`.
6b. **3D-Dioramen (VANTAGE-Stil, seit 16.11.2026)** – siehe Abschnitt unten. Blender-Clips nach `v3/dio/<name>/` rendern, dann als spec-Kinds `earthzoom` / `dio` einsetzen.
7. **Render**: `python3 engine/part2.py meta`, dann Szenen in 2 Prozessen rendern (`scene …`), dann `mix_full.py`.
8. **Export**: Masterdatei + Upload-Kopie < 299 MB (≈3,3 Mbit/s).
9. **Thumbnail (Standard = Hero-Stil, gewählt von Laurin)**: 2–3 Hero-Bilder mit gpt_image_2_6 generieren (16:9, EIN starkes Motiv rechts, dunkler leerer Raum links, dramatisches Rot/Gold-Licht, kein Text; z. B. Produkt mit leerem Preisschild, Puppenspieler-Hand, schockiertes Gesicht). Dann `thumb.json` mit `"mode":"hero"`, `lines` (2 Zeilen, letzte gelb, Frage/Schock zum Geld oder Geheimnis des Zuschauers, z. B. "YOU PAY" / "20X MORE?"), optional `tag` (Text auf leerem Preisschild; `"xy":"auto"` findet das Schild selbst und setzt den Text mittig), und `python3 engine/thumbnail.py thumb.json thumbnail.jpg`. Varianten nebeneinander ansehen, stärkste nehmen (großes Motiv, max. 4 Wörter, Zahl/Frage). Vorlage: videos/001-luxottica/thumb.json. Kein „×“-Zeichen (Anton rendert es klein) → „X“.
10. **Upload**: Video und Thumbnail per Higgsfield `media_upload` (curl PUT an upload.higgsfield.ai, dann `media_confirm`) → öffentliche URL d2ol7oe51mr4n9.cloudfront.net/… → Video: `vidiq_video_upload(url)`, Thumbnail: `vidiq_upload_image(image=url)` → imageId → `vidiq_social_post_draft_create` (YouTube, Kanal UColXdlGKvF3qRpu3nxnNR7g) → nach Laurins OK `vidiq_social_post_publish`.

## 3D-Dioramen (Earth Zoom + Polaroid-Zoom)
Miniatur-Welten im Modelleisenbahn-Look (Tilt-Shift, Staub im Gegenlicht, Teal/Orange) – aber immer aus der Ermittlungsakte heraus erzählt.
- **Bibliothek**: `engine/diorama/dio.py` (Gelände/Bergtal, Stadt, Häuser, Straßen, Autos, Miniaturfiguren mit Gelenken, Innenräume, Lampen, Texte als Texturen, Kamerafahrten, Lichtstrahl + Staub-Export). Vorlagen pro Set-Typ in `engine/diorama/scenes/` (`workshop.py` Innenraum, `aerial_town.py` Abstieg aus dem Himmel, `street_night.py` Straße nachts). Pro Video eine Vorlage kopieren und anpassen (Texte, Jahreszahl, Figuren, Requisiten, Kamera) – nie von Null bauen.
- **Rendern**: `cd engine/diorama/scenes && F1=<frames> python3 <szene>.py <work>/v3/dio/<name>` → `f_####.png` + `meta.json`. 960×540, 24 fps, 6–10 Samples, ~8–12 s/Frame auf 2 Kernen → im Hintergrund mit nohup, NIE zwei Blender-Prozesse parallel, nebenher keine anderen Rechenjobs. Vorher 1–2 Testframes (`... <out> <frame>`) ansehen.
- **Nachbearbeitung** automatisch (`engine/diorama/post.py`): Hochskalieren auf 1080p, Tilt-Shift (`focus`, `band`, `blur`), Volumenlicht + Staub (`beam`, `dust`, 0 = aus), Grade (`warm`).
- **Earth Zoom** (`["earthzoom", anchor, {"map": "map.png", "pin": [x, y], "label": ["ORT", "JAHR"], "aerial": "dio/aerial", "room": "dio/room", "dur": "scene"}]`): Karte auf dem Tisch → Pin + getippter Ort → Flug durch Wolken → Luftaufnahme sinkt bis vors Fenster → warmes Aufblenden → Innenraum. 1× pro Video, im Hook (Ort der Geschichte).
- **Polaroid-Zoom** (`["dio", anchor, {"clip": "dio/street", "caption": "NEW YORK · 2001", "stamp": "WITNESSED", "amb": "amb_workshop", "dur": "scene"}]`): Pinnwand → Kamera fährt ins Polaroid → Foto wird lebendig → am Ende einfrieren, zurück zum Polaroid, Stempel. 2–4× pro Video an Wendepunkten.
- **Sound**: Nur Geräusche, die man sieht: `D.sound()` hängt sie in Blender an Objekte (drive/walk automatisch), `engine/diorama/cues.py` mischt sie nach Entfernung (leiser, je weiter weg) und Bildposition (Stereo). Kein Wind/Rauschen. Musik in 3D-Szenen automatisch auf ~60 %. Bibliothek + Bezugsquellen: `assets/sfx/SOUNDS.md` (~55 CC0-Geräusche, 0 Credits).
- **Kosten**: 0 Credits (Blender lokal). Nur Renderzeit: ca. 1–1,5 h pro Video für 1 Earth Zoom + 2–3 Polaroid-Szenen.

## Lernschleife
Vor jedem Video LESSONS.md lesen; nach jedem Video Video-Log ergänzen und Statistiken älterer Videos auswerten.

## Kosten
~35–40 Higgsfield-Credits pro Video (Stimme ~17, Bilder ~15, Thumbnail ~2). Animation/Ton/3D-Dioramen = 0.

## Hinweise
- Fonts nach `~/.fonts` kopieren (setup_workdir.sh macht das).
- Tastatursounds key0-7.wav sind NICHT im Repo (fremde Aufnahme), setup_workdir.sh lädt sie aus Laurins Higgsfield-Speicher (Domain d2ol7oe51mr4n9.cloudfront.net muss freigegeben sein).
- Repo klonen ohne Login: `git clone --depth 1 https://github.com/laurindesruelles-max/goldsmith-pipeline` (öffentlich). Pushen geht nur in Sitzungen mit Repo-Zugriff; sonst geänderte Dateien (LESSONS.md, videos/NNN) am Ende per SendUserFile an Laurin schicken.
- Musik: `assets/music/` (Bibliothek ausbauen: 4–5 Tracks via ElevenLabs über Higgsfield).
- Der Cold Open von Video 001 ist handgebaut (`engine/case.py`); für neue Videos alle Szenen über die Spec-Engine (`part2.py`) laufen lassen und Szene 1–8 als stärkste Hook gestalten.
