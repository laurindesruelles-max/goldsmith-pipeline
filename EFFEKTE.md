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

| Karte mit Fäden (`motion` map) | Stecknadeln landen, rote Fäden spannen sich, Orte tippen sich, optional Punkte-Schwarm / rote Länder / Zähler | Schauplätze, Lieferketten, Ausbreitung | neu, ANOM-Wissen 23.11. |
| Ablauf mit Fortschrittsbalken (`motion` flow) | Geld/Akte wandert von Station zu Station, Abzweig nach unten mit Treffer | Wie ein Trick/Geldfluss funktioniert | neu, ANOM-Wissen 23.11. |
| Akte dreht sich um (`motion` flip) | Neugier-Pause, Glitch, die Akte dreht sich → Enthüllung in Rot | Die eine große Enthüllung | neu, ANOM-Wissen 23.11. |
| Große Zahl (`motion` counter) | Zahl zählt hoch, dahinter fliegen Geldscheine/Akten | Umsatz, Schaden, Strafe | neu, ANOM-Wissen 23.11. |
| Raster (`motion` grid) | Viele Kärtchen legen sich, einzelne rot, Zahl daneben | Menge (Filialen, Opfer, Firmen) | neu, ANOM-Wissen 23.11. |
| Handy-Chat (`motion` phone) | Nachrichten poppen auf, Zitat tippt sich | Belegte Chats/Mails; sonst als RECONSTRUCTION kennzeichnen | neu, ANOM-Wissen 23.11. |
| Verschlüsselung (`motion` cipher) | Text zerfällt in Zeichen | Geheimhaltung, Codes | neu, ANOM-Wissen 23.11. |
| Aktenstapel (`motion` stack) | Verfahren stapeln sich, Stempel-Symbol knallt drauf, Frage tippt | Prozesse, offene Fragen am Schluss | neu, ANOM-Wissen 23.11. |

**Erweiterung 23.11.2026 (ANOM-Stilprobe):** Die `motion`-Bausteine kommen **zusätzlich** zu allen bisherigen Effekten (nichts wird ersetzt). Ziel: deutlich mehr 2D-Animation, etwa alle 2–4 s ein neues Bild, 6–12 motion-Clips pro Video. Doku: `engine/motion_fx.py`. Demo: `Goldsmith_Motion_Bausteine.mp4` (23.11.2026 an Laurin).

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
