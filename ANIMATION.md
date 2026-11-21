# Goldsmith – Animations-Möglichkeiten (Laurin, 21.11.2026)

Ergänzt `EFFEKTE.md` (abgenommener Kern-Katalog) um alles, was zur Nische passt: Wirtschafts- und Konzern-Ermittlungen, Geldflüsse, Betrug, Machtstrukturen. Alles spielt weiter im **Ermittlungsraum** (Schreibtisch, Akte, Pinnwand). Exklusiv-Regeln bleiben: kein Zeitungs-Wirbel (Nachtausgabe), kein Miniatur-/Tilt-Shift-Look (Unterbau). Für jedes Skript gilt das Bild-Drehbuch aus `HANDWERK.md`.

## Zeit und Geschehen in dieser Nische
- **Zeit:** Datum immer **exakt** (Tag, Monat, Jahr aus der Quelle), getippt oder als Kalender. Bei Abläufen über Monate/Jahre: Zeitstrahl am Faden. Uhrzeit nur, wenn belegt.
- **Geld:** Jeder Betrag **exakt** und mit Quelle, als Zahl auf Papier; Geldwege immer als sichtbarer Weg (Faden, Route), nie nur gesagt.
- **Geschehen:** Entscheidende Momente (Meeting, Unterschrift, Anruf) als Rekonstruktion im Polaroid zeigen – realistisch, aber als Rekonstruktion erkennbar.
- **Neugier-Lücke:** Schwärzung, umgedrehte Karte, verdecktes Polaroid, Lupe, die noch nicht angekommen ist.

## Animations-Katalog (zusätzlich zu EFFEKTE.md)
| Animation | Was passiert | Wann | Genauigkeit | Werkzeug | Status |
| --- | --- | --- | --- | --- | --- |
| Geldspur | Scheine/Münzen wandern am roten Faden von Nadel zu Nadel, der Betrag zählt mit | Geldfluss, Bestechung, Steuertrick | exakt | PIL/Blender | bauen |
| Firmengeflecht | Karteikarten (Briefkastenfirmen) werden angepinnt, Fäden verzweigen sich Ebene für Ebene bis zum Eigentümer | Konzernstruktur, Verschleierung | schema | Manim-Layout → Papier-Look | bauen |
| Zeitstrahl am Faden | Ein Faden spannt sich quer über die Wand, datierte Karten springen an ihre Stelle, Kamera fährt mit | Chronologie, Monate/Jahre | exakt | PIL | bauen |
| Abreißkalender | Kalenderblätter auf dem Tisch reißen ab bis zum Stichtag | Zeitsprung, Frist | exakt | PIL | bauen |
| Lupe | Eine Lupe gleitet über ein Dokument und vergrößert das entscheidende Detail | Fund im Kleingedruckten | exakt | PIL | bauen |
| Beweis-Ausdruck | E-Mail/Chat-Ausdruck rutscht aus dem Drucker, Zeilen werden markiert | belegte Nachricht | exakt | PIL (`doc`-Variante) | bauen |
| Ticker-Band | Ein Papier-Kursband rollt sich ab, der Kurs fällt/steigt mit | Börsenkurs, Crash | exakt | PIL (`chart`-Variante) | bauen |
| Aktenstapel wächst | Akten türmen sich auf dem Tisch, Zahl der Fälle tickt mit | Ausmaß, Anzahl | exakt | Blender | bauen |
| Rekonstruktion im Polaroid | Im Foto spielt sich der Moment in realistischem 3D ab (Meeting, Unterschrift, Übergabe), Figuren ohne Gesicht | Schlüsselszene | exakt (belegt) | Blender | steht als Diorama, Figuren bauen |
| Schattenriss | Unbekannte Person als Silhouette hinter Milchglas im Polaroid | unbekannter Täter, Insider | stimmung | PIL/2,5D | bauen |
| Foto erwacht | Ein Archivfoto an der Wand bekommt Tiefe, Rauch/Licht bewegen sich darin | historisches Foto | exakt | depth25d | steht (`parallax`), ausbauen |
| Verdeckte Karte | Eine Karteikarte liegt umgedreht an der Wand, wird erst bei der Auflösung umgedreht | offene Frage | – | PIL | bauen |
| Weltkarte mit Nadeln | Papier-Weltkarte, Nadeln für jedes Land, Fäden zu Steueroasen | internationale Struktur | exakt | PIL (`route`) | steht, erweitern |
| Diagramm baut sich auf | Balken/Linien werden mit Lineal auf Millimeterpapier gezogen | Vergleich, Entwicklung | exakt | Manim → Papier-Look | steht (`chart`), Manim-Präzision |

## Werkzeuge (alle ohne Credits, getestet 21.11.2026)
| Werkzeug | Wofür | Einrichten |
| --- | --- | --- |
| Blender (`bpy`) | echtes 3D, Physik (Rigid Body, Flüssigkeit, Stoff, Partikel), Geometry Nodes für Wachstum/Aufbau, Grease Pencil für gezeichnete Linien im Raum, Rigging für Figuren | `pip install bpy` (setup.sh) |
| 2,5D-Tiefe (`depth25d.py`, Depth Anything) | jedes Standbild in Ebenen zerlegen, Kamera fährt mit Tiefe hindurch, Ebenen bewegen sich einzeln | im Goldsmith-/Unterbau-Repo vorhanden |
| PIL + numpy + ffmpeg | eigene Motion-Grafik, Partikel, Licht, Übergänge, Compositing | vorhanden |
| Manim | exakte, animierte Diagramme, Netzwerke, Abläufe, Formeln, Zählwerke – danach im Kanal-Look eingefärbt | `apt-get install -y libpango1.0-dev libcairo2-dev && pip install manim` |
| rlottie | Lottie-Vektoranimationen (Icons, kleine Abläufe) als Vorlage, immer im Kanal-Stil nachgezeichnet | `pip install rlottie-python` |
| Pixabay, Wikimedia, Archive | echte Clips und Fotos, nur innerhalb der Kanal-Welt eingebaut (siehe HANDWERK.md) | `stock.py`, `sources.py` |
| Higgsfield | nur KI-**Bilder** (0,25 Credits), Freistellen, 3D-Modell aus Bild. **Keine KI-Videoclips** (Laurin 21.11.2026) | – |

Status in den Tabellen: **steht** = in der Engine vorhanden · **bauen** = freigegeben (Laurin 21.11.2026), beim ersten Einsatz als Baustein in die Engine aufnehmen und kurz Stilprobe an Laurin.
