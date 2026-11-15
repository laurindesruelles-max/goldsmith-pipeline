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
7. **Render**: `python3 engine/part2.py meta`, dann Szenen in 2 Prozessen rendern (`scene …`), dann `mix_full.py`.
8. **Export**: Masterdatei + Upload-Kopie < 299 MB (≈3,3 Mbit/s).
9. **Thumbnail (Standard = Hero-Stil, gewählt von Laurin)**: 2–3 Hero-Bilder mit gpt_image_2_6 generieren (16:9, EIN starkes Motiv rechts, dunkler leerer Raum links, dramatisches Rot/Gold-Licht, kein Text; z. B. Produkt mit leerem Preisschild, Puppenspieler-Hand, schockiertes Gesicht). Dann `thumb.json` mit `"mode":"hero"`, `lines` (2 Zeilen, letzte gelb, Frage/Schock zum Geld oder Geheimnis des Zuschauers, z. B. "YOU PAY" / "20X MORE?"), optional `tag` (Text auf leerem Preisschild; `"xy":"auto"` findet das Schild selbst und setzt den Text mittig), und `python3 engine/thumbnail.py thumb.json thumbnail.jpg`. Varianten nebeneinander ansehen, stärkste nehmen (großes Motiv, max. 4 Wörter, Zahl/Frage). Vorlage: videos/001-luxottica/thumb.json. Kein „×“-Zeichen (Anton rendert es klein) → „X“.
10. **Upload**: Video und Thumbnail per Higgsfield `media_upload` (curl PUT an upload.higgsfield.ai, dann `media_confirm`) → öffentliche URL d2ol7oe51mr4n9.cloudfront.net/… → Video: `vidiq_video_upload(url)`, Thumbnail: `vidiq_upload_image(image=url)` → imageId → `vidiq_social_post_draft_create` (YouTube, Kanal UColXdlGKvF3qRpu3nxnNR7g) → nach Laurins OK `vidiq_social_post_publish`.

## Lernschleife
Vor jedem Video LESSONS.md lesen; nach jedem Video Video-Log ergänzen und Statistiken älterer Videos auswerten.

## Kosten
~35–40 Higgsfield-Credits pro Video (Stimme ~17, Bilder ~15, Thumbnail ~2). Animation/Ton = 0.

## Hinweise
- Fonts nach `~/.fonts` kopieren (setup_workdir.sh macht das).
- Tastatursounds key0-7.wav sind NICHT im Repo (fremde Aufnahme), setup_workdir.sh lädt sie aus Laurins Higgsfield-Speicher (Domain d2ol7oe51mr4n9.cloudfront.net muss freigegeben sein).
- Repo klonen ohne Login: `git clone --depth 1 https://github.com/laurindesruelles-max/goldsmith-pipeline` (öffentlich). Pushen geht nur in Sitzungen mit Repo-Zugriff; sonst geänderte Dateien (LESSONS.md, videos/NNN) am Ende per SendUserFile an Laurin schicken.
- Musik: `assets/music/` (Bibliothek ausbauen: 4–5 Tracks via ElevenLabs über Higgsfield).
- Der Cold Open von Video 001 ist handgebaut (`engine/case.py`); für neue Videos alle Szenen über die Spec-Engine (`part2.py`) laufen lassen und Szene 1–8 als stärkste Hook gestalten.
