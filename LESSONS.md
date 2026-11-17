# Goldsmith – Lernbuch (wird bei JEDEM Video gelesen und ergänzt)

Ziel: Jedes Video ist besser als das letzte – Schnitt, Spannung, Sound, Thumbnail.

## Feste Regeln aus Laurins Feedback
- **LÄNGE: JEDES Video MUSS über 8 Minuten lang sein (ganz wichtig, Laurin 15.11.2026).** Ziel 9–10 Min. Vor dem Rendern Gesamtdauer aus timing.json prüfen; liegt sie unter 8:30, Szenen/Kapitel ergänzen.
- **Pflicht-Ende**: Kommentar-Frage + „Subscribe and hit the bell“ (Kommentar-Feld, Subscribe-Button, Glocke im Bild).
- Keine rot/blauen 3D-Figuren oder Mannequins, keine reine Diashow. Viele Bewegungsgrafiken, Effekte auf jedem Element. AUSNAHME (Laurin 16.11.2026): Miniaturfiguren in den 3D-Dioramen (Modelleisenbahn-Look, gedeckte echte Farben, klein im Bild) sind ausdrücklich gewünscht.
- Daten und Orte immer als Schreibmaschinentext mit mechanischem Tastatursound (assets/sfx/key0-7, Lautstärke Faktor 0.75 – vorher zu leise/zu laut).
- Musik muss spannend sein (ElevenLabs-Tracks, nie selbst synthetisiert). Pro Kapitel passender Track (spec "music").
- Spannung braucht Pausen: nach jeder großen Enthüllung 0,8–1,5 s Stille (spec "beats"), Musik taucht ab, dann Hit.
- Thumbnail: Hero-Stil, EIN großes Motiv, 2 Zeilen, Zahl oder Frage zum Geld des Zuschauers. Text auf Preisschild mittig (tag xy "auto").
- Sound sparsam (15.11.): Kapitel bekommt genau EINEN Hit auf der Karte – kein Riser davor, kein Pausen-Hit in den 4 s davor. Kein Whoosh bei Text-Pops oder normalen Schnitten; Whoosh nur noch bei großen Vollbild-Effekten (leise). Text-Pops nur leiser Slap.

## Echte Quellen (Laurin 16.11.2026: „echte Fakten, echte Artikel, echte Bilder – nur was erlaubt ist“)
- Pro Video 6–12 echte Belege einbauen: Archivfotos (`photo`), echte Dokument-Auszüge (`doc` mit wörtlichem Zitat + `source`), echte Überschriften als kurzes Zitat (`news` + `source`), Diagramme aus echten Zahlen (`chart` + `source`). Regeln: engine/sources.py. Bildnachweise in die Beschreibung. Im Zweifel weglassen.

## Schnitt & Spannung nach VANTAGE-Vorbild (Laurin 16.11.2026, Referenz: VANTAGE „The FBI's Most Wanted Man Worked for the FBI“)
- **Ein Satz = ein Bild**: Skript so schreiben, dass jeder Satz ein konkretes, zeigbares Detail hat (Telefon, Zettel an der Tür, Aufzuganzeige, Akte). Das Bild zeigt genau das, was gerade gesagt wird. Shots 2–7 s.
- **Trichter-Hook**: groß → klein (Karte → Stadt → Gebäude → Fenster → Detail). Dafür der Earth Zoom.
- **Ruhige Kamera, Bewegung im Bild**: lieber Licht flackert, Auto fährt vor, Figur geht – statt wilder Kamerafahrten. Harte Schnitte.
- **Rhythmus**: Spannung → Atempause mit Akte/Dokument → Spannung. Vor jeder großen Enthüllung kurz Stille (beats).
- **Staub im Gegenlicht** nur in Innenräumen/Archiv/Werkstatt mit Lichtstrahl (Fenster, Lampe) – nicht in hellen Außenszenen. Wenige, langsame Partikel.
- **3D-Dosierung**: 1 Earth Zoom (Hook) + 2–4 Polaroid-Zooms an Wendepunkten ≈ 10–15 % der Laufzeit. Der Rest bleibt Ermittlungsakte.
- **Sound in 3D-Szenen**: KEIN Rausch-/Wind-Teppich (Laurin 16.11.: Rauschen gefiel nicht). Nur Geräusche zu dem, was man sieht (Auto fährt vor = Autogeräusch, eher leise), automatisch nach Entfernung/Stereo. Bibliothek: assets/sfx/SOUNDS.md. Tastatursound bleibt unverändert (Laurin 16.11.: „mein Tastatursound bleibt ganz normal“).

## Effekt-Kandidaten (Showreel 15.11.2026, engine/effects_showreel.py)
Parallax-3D, Dokument-Zoom + Textmarker, Schwärzung aufdecken, animiertes Diagramm, Landkarte mit Routen, Vorher/Nachher-Splitscreen, Übergänge (Film Burn, Glitch, Paper Wipe), Zeitungs-Wirbel. Status: von Laurin ALLE 8 freigegeben (15.11.2026) und in engine/effects.py eingebaut. Pro Video 4–7 dieser Vollbild-Effekte einsetzen, jeden Typ höchstens 2×, passend zum Inhalt (Kursverlust → chart, Enthüllung eines Namens → redact, internes Dokument/Zitat aus Akten → doc, Lieferkette/Orte → route, Wandel → split, Übernahme/Skandal → news, emotionale Schlüsselszene → parallax). Übergänge laufen automatisch an Schnitten.
Neue Sounds in assets/sfx: highlighter, paper_tear, glitch, film_projector, coins, heartbeat, flash, sub_drop.

## Musikbibliothek (assets/music)
| Datei | Stimmung | Wofür |
|---|---|---|
| music_tension.mp3 | angespannte Ermittlung | Cold Open, Standard |
| suspense_pulse.mp3 | dunkel, pulsierend, tickend | Konflikt-/Kriegskapitel, Gerichtsfälle |
| epic_empire.mp3 | episch, Trommeln, Bläser | Aufstieg, Übernahmen, „The giant gets bigger“ |
| emotional_piano.mp3 | Klavier, melancholisch | Herkunftsgeschichte, Tod, Niedergang, Verdict |
Neue Tracks ergänzen, wenn Wiederholung auffällt (ca. 17 Credits / 120 s).

## Dramaturgie-Checkliste pro Video
- [ ] Hook (Szene 1–6) mit Wendung („It isn't.“) + Pause danach
- [ ] Titel-Reveal mit Riser → Braam
- [ ] 3–6 beats insgesamt (nicht mehr – sonst zäh)
- [ ] Musikwechsel an Kapitelgrenzen passend zur Stimmung
- [ ] Jede Szene 1–3 Overlay-Elemente; Zahlen als counter, Daten/Orte als typed
- [ ] Stills vor dem Rendern prüfen (Überlappungen: typed-Box + quote nicht gleichzeitig)

## Auswertung (ab 48 h nach Veröffentlichung)
Bei jedem Lauf: Statistiken der letzten 1–2 veröffentlichten Videos holen (vidiq_video_stats / vidiq_channel_analytics: Aufrufe, Klickrate, durchschnittliche Wiedergabedauer, Absprungstellen falls verfügbar) und hier unter „Video-Log“ eintragen + 1–3 konkrete Konsequenzen für das nächste Video.

## Technik-Hinweise
- Automatischer Lauf am 15.11. scheiterte am privaten Repo → Repo ist jetzt öffentlich, Tastatursounds liegen extern (setup_workdir.sh lädt sie).
- Higgsfield: max. ~6 gleichzeitige Jobs je Typ, sonst 429 → in 6er-Batches arbeiten.

## Video-Log
| # | Video | Datum | Thumbnail | Ergebnis | Erkenntnis |
|---|---|---|---|---|---|
| 002 | Why Luxury Brands Burn Their Own Clothes | 17.11.2026 (S3GMEPAgqas) | Hero „THEY BURNED £28.6 MILLION“ | (noch offen) | Erstes Video mit allen Effekten, Kapitelmusik und Pausen. Länge ~8 Min (kürzer als 001). Thumbnail-Heroes mit Handtaschen ähneln echten Designermodellen (Birkin/Chanel) → solche Motive meiden. Neu hochgeladen mit ruhigerem Sound (1 Kapitel-Hit, kaum Whoosh). |
| 001 | The Company That Secretly Owns Your Glasses | 15.11.2026 | Hero A „YOU PAY 20X MORE?“ | (noch offen) | Pilot. Musik war nur 1 Track in Schleife; keine Pausen. Ab 002: Kapitel-Musik + beats. |

## Video 003 – GTA 6 (16.11.2026, Veröffentlichung 19.11.)
- Faktencheck-Agent kam nicht zurück → nicht warten, riskante Szenen selbst gegen Primärquellen prüfen (Transkript, SEC, Gericht) bevor sie vertont werden.
- Zitate nur nach wörtlicher Prüfung im Transkript; im Zweifel umschreiben statt zitieren.
- Keine „Fantasie-Kurven“ für Einzelwerte (Anteil, Quartalsrückgang) → counter statt chart.
- Master-Mix kann 0,0 dBFS Spitze haben → Upload-Kopie immer mit loudnorm I=-14:TP=-1.5.
- Thumbnail: Thema („GTA 6“) muss im Bild stehen; nur als eigener Text, nie Logo. Laurin mag Miami-Neon-Look ohne Glow hinter der Schrift.
- Warte-Schleifen nie mit `pgrep -f "<muster>"` in `sh -c` (findet sich selbst).
- effects.py-Änderungen vor dem Lauf in v3 kopieren und importieren (endcard-Bug: SOUNDS vor Definition benutzt).

## Feedback Laurin zu 003 v1 (16.11.) → Regeln ab jetzt
- KEINE Anfangsmusik / kein music_tension mehr (zu anstrengend). Musik ab Kapitel 1.
- KEIN weißer Wipe-Balken; Übergänge selten (TRANS in effects.py).
- Bass-Hit (braam/boom) NUR bei Kapitelkarten.
- Nie nur Standbild + Zoom: Standard ist 2.5D-Parallaxe (engine/depth25d.py, Depth Anything V2 ONNX, kostenlos),
  Atmosphäre per spec "atmo" (rain/dust) + "flicker", zweites Bild N_b.png pro Szene (jeder 2. Schnitt),
  Schnitte auch an Kommas bei langen Einstellungen, animierte Daten-Grafiken (engine/graphics.py: bars, breakdown, timeline, flow).
- Bildwelt abwechseln: nicht alles „dunkler Schreibtisch mit Lampe“ – Straßen, Städte, Studios, Gericht, Börse, Neon.
- Laurin will lieber kostenlose Lösungen statt KI-Videoclips (Kling ~7,5 Credits/Clip nur nach Rückfrage).
- Musik (16.11.): Laurin will Krimi-Stil. Gut: crime_archive (True-Crime-Klavier, Cello, Tick-Puls), suspense_pulse, epic_empire, emotional_piano; ok: crime_pulse, night_intro. NICHT: music_tension (gelöscht), Film-Noir-Jazz, Military/Lobby-Synth. Neue Tracks per elevenlabs_music_v2_5 (~22 Credits/150 s), auf -15,7 LUFS normalisieren.
- 16.11. abends: Laurin will Bewegung IM Bild, aber kostenlos → engine/cinemagraph.py (Licht pulsiert/flackert, Glow atmet,
  nasse Böden schimmern, Lichtstrahlen aus Lampen, ziehender Nebel, Glanzlicht über Geld, Handyblitze, Scheinwerfer-Schwenk).
  spec "fx": {"N": ["wet","flash","cars","money","screens","fog","cold"]}. Fallende Geld-Partikel sahen billig aus → ersetzt durch Glanzlicht.
- Jede Einstellung eigenes Bild: N, N_b, N_c, N_d (shot_key in part2.py). gpt_image_2_6 kostet nur 0,25 Credits/Bild → ruhig viele Bilder.
- Bereits bezahlte KI-Clips liegen in work/vid/<key>.mp4 und werden automatisch statt des Standbilds benutzt.
- KI-Videoclips (Seedance 2.0 Mini 720p 5 s = 5 Credits) hat Laurin für ganze Videos abgelehnt (zu teuer).
- Musik-Dramaturgie (Laurin 16.11.): nie 2–3 Min. derselbe Track. Jedes Kapitel eigener Track (spec "music" pro Kapitel,
  bei langen Kapiteln Wechsel in der Mitte), vor jedem Wechsel ausblenden + 0,5 s Stille, neuer Track setzt mit der Kapitelkarte ein.
  Bewusste Musikpausen an starken Aussagen: spec "music_rests": {"N": [start_offset, dauer]}. Kapitelkarte steht 4,4 s (CARD_T).
- Vollbild-Effekte, deren Anker < 1 s nach Szenenstart liegt, starten bei 0 (kein Aufblitzen des Grundbilds, Laurin 17.11.).
- Reinzoomen braucht Sound (Laurin 17.11.): Earth-Zoom = riser + whoosh beim Durchstoßen + whoosh in den Raum; Polaroid-Zoom = shutter + whoosh.
- Musik (Laurin 17.11.): KEINE neuen Tracks pro Video erzeugen – nur die feste Bibliothek in assets/music nutzen. Neue Tracks nur, wenn Laurin es ausdrücklich verlangt (kostet Credits).
- Echtes Videomaterial: Pixabay statt Pexels (Pexels vergibt derzeit keine API-Schlüssel). engine/stock.py, Schlüssel nur zur Laufzeit (PIXABAY_KEY), bei Laurin erfragen.
- Sounddesign nach Referenzen (MagnatesMedia, VANTAGE; vidIQ-Analyse 17.11.): Daten-Grafiken = kurze, saubere UI-Blips pro Wert, Musik während Daten fast weg (Ducking 28 %),
  Zahlen = Zähl-Sound + weicher Impact, Text-Pops = leiser Air-Whoosh (statt „slap“), Karten-Pins = Pin + weicher Sub-Hit, Geld = Münze/Kasse, Kalender = Blatt-Flip.
  Neue CC0-Sounds (SFXMint/HF): ui_blip, ui_toast, ui_send, ui_drag, data_process, count_up, whoosh_soft, impact_soft, reveal_hit, riser_short, scan, logo_reveal, news_sting, bills_count, coin_drop, card_flip, chime, camera_snap.
- Neue Effekte: kinetic (Wort für Wort, Schlüsselwort gold + rote Linie), phone (Push-Nachricht), calendar (Abreißkalender), ticker (Laufband + Schlagzeile),
  fx "spot" (Spotlicht), Lichtleck an jedem ~3. Schnitt. Ticker nie mit erfundenen Kursen – nur belegte Werte.
- engine/demo_mix.py: schneller Probe-Mix einzelner Szenen (Stimme + Sounds + Musik) ohne Gesamt-Mix.
