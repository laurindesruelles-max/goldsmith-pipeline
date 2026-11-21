# Goldsmith – Handschrift und Effekte (von Laurin abgenommen am 20.11.2026)

Gemeinsame Regeln: `HANDWERK.md`. Hier steht nur, was Goldsmith von den anderen Kanälen unterscheidet.
Weitere freigegebene Animationsarten für die Nische und die Bild-Drehbuch-Regeln: `ANIMATION.md` (21.11.2026).

## Erkennungsmerkmale
| | Goldsmith |
| --- | --- |
| Sprache | Englisch |
| Welt | Ermittlungsraum: Schreibtisch, Akte, Pinnwand. Das ganze Video spielt dort |
| Technik | 2,5D-Papier und Fotos, dazu Blender-3D nur im Polaroid (realistisch, **kein** Miniatur- oder Tilt-Shift-Look, der gehört Unterbau) |
| Farben | warmes Lampenlicht, Rot (Faden), Gold |
| Kamera | gleitet über Tisch und Wand, kurzer Ruck beim Stempel |
| Tempo | 4–5 s, ruhig und bedrohlich |
| Schrift | Schreibmaschine (Special Elite), Stempel (Anton) |
| Übergang | Schwenk zum nächsten Foto an der Wand |
| Zahlen und Karten | auf Papier gedruckt, mit Textmarker, Papierkarte mit Nadeln und Faden |
| Musik | True-Crime-Klavier, wird vor Kapiteln leiser und wechselt dann. Kein Noir-Jazz |
| Stimme | Alistair |

## Effekt-Katalog (nur diese verwenden)
| Effekt | Was passiert | Wann | Status |
| --- | --- | --- | --- |
| Wand wächst | Jedes Kapitel ergänzt die eine Pinnwand, am Kapitelende fährt die Kamera zurück und zeigt alles | Kapitelende, Schluss | neu, Stilprobe 20.11. |
| Akte wird zugeschoben | Eine Akte rutscht über den Tisch, das Deckblatt zeigt den Kapiteltitel | Kapitelstart | neu, Stilprobe 20.11. |
| Ort und Datum tippen | Schreibmaschine tippt „MILAN, 1961“ | neuer Ort, neue Zeit | steht (`typed`) |
| Polaroid anpinnen | Ein Foto fällt auf die Wand, die Nadel sitzt | neue Person oder Firma | steht |
| Roter Faden | Ein Faden spannt sich von Nadel zu Nadel | Verbindung, Geldfluss | steht |
| Stempel | Stempel knallt, die Kamera ruckt | Enthüllung, Urteil | steht (gehört nur Goldsmith) |
| Schwärzung | Balken legen sich über Zeilen, eine bleibt frei | Geheimes | steht (`redact`) |
| Textmarker | Ein Marker zieht über den Satz in einem Dokument | Zitat aus einer Quelle | steht (`doc`) |
| Zahl auf Papier | Die Zahl tickt auf einem Kontoauszug hoch und bremst ab | harte Zahl | steht (`counter`) |
| Papier-Diagramm | Eine Kurve wird auf Millimeterpapier gezeichnet | Entwicklung | steht (`chart`) |
| Route mit Nadeln | Faden läuft über eine Papierkarte | Weg von Waren oder Geld | steht (`route`) |
| Earth Zoom | Roter Punkt, Zoom vom All bis in den Raum | neuer Schauplatz | steht |
| Diorama im Polaroid | Die Kamera taucht in ein Foto ein, dort steht die Szene in 3D (realistisch) | 2–3 Schlüsselszenen | steht, Look anpassen |
| Vorher/Nachher | Zwei Fotos, eine Linie teilt sie | Vergleich | steht (`split`) |
| Lampe schwenkt | Licht wandert über die Wand, die Ränder werden dunkel | Spannung vor einer Wendung | neu, Stilprobe 20.11. |

**Raus:** Zeitungs-Wirbel (`news`), denn Zeitung gehört Nachtausgabe. Artikel stattdessen als Ausschnitt anpinnen. Raus ist auch der weiße Balken-Übergang.

Stilprobe: `stilprobe_goldsmith.mp4` (20.11.2026, an Laurin geschickt). Sounds folgen nach dem Casting (`doku-ohren`).

## Sound je Effekt (Stand 20.11.2026, Demo geschickt (20.11.2026), nur Laurins abgenommene Goldsmith-Sounds)
Geplant nach dem Grundsatz aus `HANDWERK.md`: erst festlegen, wo überhaupt ein Sound hingehört, dann je Stelle genau einen. Skripte: `engine/stilproben/ton_*.py`.

| Effekt | Sound |
| --- | --- |
| Akte wird zugeschoben | paper_slide + leiser whoosh + paper |
| Ort und Datum tippen | key0–6 |
| Polaroid anpinnen | shutter + slap + pin |
| Roter Faden | zip |
| Stempel | Musik setzt aus, stamp + braam + boom |
| Wand wächst/Rückzoom | whoosh |
| Lampe schwenkt | lever leise, am Ende sub_drop leise |
| Spannung | tick einmal pro Sekunde, sehr leise |
| Musik | crime_pulse, kein Musikstart in den ersten Sekunden |
