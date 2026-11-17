# Gemeinsame Sound-Bibliothek (alle Kanäle)

Laurins ausgewählte Sounds für **alle** YouTube-Kanäle (Goldsmith Productions, Meisterwerk, Unterbau …).
Eine Stelle für alle: Neue Sounds von Laurin kommen IMMER hierher (nicht in das sfx-Verzeichnis eines einzelnen Kanals),
mit Zeile in dieser Tabelle.
**Nur Geräusche, keine Musik:** Musik hat jeder Kanal selbst (Goldsmiths Krimi-Musik passt nur zu Goldsmith, Laurin 17.11.2026). Alle Dateien: WAV, 48 kHz, Stereo, Anfangsstille entfernt, Spitze normalisiert.

## Einbinden in ein Kanal-Projekt
Das Repo ist öffentlich, kein Login nötig. In der setup.sh des Kanals (nach dem Kopieren der eigenen Sounds):

```sh
curl -sSfL https://raw.githubusercontent.com/laurindesruelles-max/goldsmith-pipeline/main/sound-library/get.sh | sh -s -- "$WORK/sfx"
```

`get.sh` lädt alle Sounds dieser Bibliothek in den angegebenen Ordner (überschreibt gleichnamige Dateien).
Goldsmith nutzt sie direkt aus dem Repo (engine/setup_workdir.sh).

## Herkunft (Lizenz-Nachweis)
Laurin (17.11.2026): Alle Sounds stammen aus seiner Sammlung mit ~1000 Effekten, außer wo unten eine andere Quelle steht
(dort lizenzfreie „No Copyright“-Effekte bzw. eigene Aufnahme).

| Name | Herkunft / Bearbeitung | Wofür (Laurins Entscheidung 17.11.2026) |
|---|---|---|
| pin_pop | von Laurin geschickt (17.11.2026): „Pop Sound Effect“, Quelle youtube.com/shorts/dFGHrYjRd7U, der 2. Pop der Datei (bei 5,1 s), 0,27 s, Spitze -3 dB | Pins auf der Landkarte (route, Earth-Zoom) |
| diagram_whoosh | von Laurin geschickt (17.11.2026): „6 - whoosh swoosh - short“, 0,75 s, Spitze -3 dB | Diagramme: Balken wächst, Geldfluss, Aufteilung |
| paper_slide | von Laurin geschickt (17.11.2026): „Paper Slide – Sound Effect“, Schiebe-Geräusch 0,56 s herausgeschnitten, Spitze -3 dB | Endkarte: Kommentarfeld schiebt sich rein; Schwärzung: jeder schwarze Balken gleitet weg |
| zoom_riser | von Laurin geschickt (17.11.2026): „Riser Sound Effect – No Copyright, Free To Use“, Vorbild youtube.com/shorts/EJ7IDvA3VnI; erste 0,7 s (fast still) entfernt, 4,76 s, Spitze -2 dB | Earth-Zoom: Karte -> 3D, läuft über die ganze Kartenphase |
| news_spin | von Laurin geschickt (17.11.2026, Datei 08.wav aus seinem Effekt-Paket), auf 1,75 s gekürzt, Spitze -3 dB | Zeitung wirbelt rein (news) |
| marker_stroke, marker_stroke2 | von Laurin selbst aufgenommen (17.11.2026, „asmr marker sounds“), zwei 0,55-s-Striche aus der Aufnahme, gleich laut (-19 dB) | Textmarker-Strich in der Akte (doc) |
| data_loading | von Laurin geschickt (17.11.2026): „Loading Animation Sound Effect (Free Download, No Copyright)“, Vorbild youtube.com/shorts/yFD-XAaKf54; gekürzt auf 1,68 s, Spitze -1 dB | Kurs-Grafik (chart): Linie zeichnet sich |
| phone_notify | von Laurin geschickt (17.11.2026, aus seinem Effekt-Paket; Notification.wav, auf 1,06 s gekürzt, Spitze -1 dB) | Handy-Push-Nachricht (Effekt phone) |
| text_click | von Laurin geschickt (17.11.2026, aus seinem Paket mit ~1000 Effekten (Laurin: alle nicht anders genannten Sounds stammen aus dieser Sammlung); Datei 7dd9c3b3-06.wav, Anfangsstille entfernt, Spitze auf -0,9 dB) – ersetzt den Meisterwerk-Klick | Klick bei Schlagwörtern und Text-Einblendungen (Laurin: „sogar besser“) |
