# Goldsmith – Lernbuch (wird bei JEDEM Video gelesen und ergänzt)

> **Seit 20.11.2026 zuerst lesen:** `HANDWERK.md` (Regeln für alle Kanäle) und `EFFEKTE.md` (Handschrift und erlaubte Effekte dieses Kanals, von Laurin abgenommen). Bei Widerspruch gelten diese beiden Dateien.


Ziel: Jedes Video ist besser als das letzte – Schnitt, Spannung, Sound, Thumbnail.

## Feste Regeln aus Laurins Feedback
- **LÄNGE: JEDES Video MUSS über 8 Minuten lang sein (ganz wichtig, Laurin 15.11.2026).** Ziel 9–10 Min. Vor dem Rendern Gesamtdauer aus timing.json prüfen; liegt sie unter 8:30, Szenen/Kapitel ergänzen.
- **Pflicht-Ende**: Kommentar-Frage + „Subscribe and hit the bell“ (Kommentar-Feld, Subscribe-Button, Glocke im Bild).
- Keine rot/blauen 3D-Figuren oder Mannequins, keine reine Diashow. Viele Bewegungsgrafiken, Effekte auf jedem Element. AUSNAHME (Laurin 16.11.2026): Miniaturfiguren in den 3D-Dioramen (Modelleisenbahn-Look, gedeckte echte Farben, klein im Bild) sind ausdrücklich gewünscht.
- Daten und Orte immer als Schreibmaschinentext mit mechanischem Tastatursound (assets/sfx/key0-7, Lautstärke Faktor 0.75 – vorher zu leise/zu laut).
- Schlagwörter und andere Text-Einblendungen (pop, words, brands, chain-Labels) bekommen den Klick "text_click" (Gain 0.42; seit 17.11. Laurins eigener Sound aus seinem Effekt-Paket, vorher Meisterwerk-Klick) statt slap (Laurin 17.11.2026). Einzelner Tastenanschlag wurde getestet und abgelehnt („hört sich nicht gut an“). Stempel, Polaroids und Zettel behalten ihre eigenen Sounds.
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
- **Sound-Herkunft absichern** (Laurin 17.11.): Jeder Sound, der nicht CC0 ist, bekommt in sound-library/_herkunft/ einen Nachweis (Link, Kanal, Lizenzangabe, Datum, Originaldatei). Kamera-Auslöser `shutter` = Laurins Wahl (YouTube „No Copyright“-Pack, Klick 4). Sound-Plan: UI-Sounds einmalig von Laurin wählen lassen, Szenengeräusche aus Profi-Bibliothek (Sonniss) automatisch.
- **Sound-Änderung bestätigen** (Laurin 17.11.): Nach jedem neuen/getauschten Sound den gewählten Sound selbst (nur die Audiodatei) zum Gegenhören schicken – keinen Bild-Clip.
- **Effekt `desktop` freigegeben** (Laurin 17.11.): Ermittler-PC, Mauszeiger klickt Fallakte an (mouse_click), Fenster mit Szenenbild + getippten Fakten + Stempel. Einsetzen, wenn eine Akte/ein Dokument/ein Leak „geöffnet“ wird – ca. 1× pro Video.
- **Preisschild-Sound** (Laurin 17.11.): Wenn ein Preis/Preisschild/Preisangabe aufploppt (wie die Brillen-Preisschilder im Luxottica-Video) → `price_tag` (Lautstärke 0.55), kurz nach dem Erscheinen (+0.06 s).

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
- [ ] Hook (Szene 1–6) mit Wendung („It isn't.“) + Pause danach; Thema + Thumbnail-Motiv in 0–5 s, Hook ≤ 40 s (Hook-Regeln unten)
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
| 004 | How GTA 5 Became a 13-Year Money Machine | Entwurf 22.11.2026, geplant 23.11. 17:00 | Hero „GTA 5 / 13 YEARS. / STILL PRINTING.“ (Druckerpresse mit Spielhülle), Variante B „STILL PAYING?“ | (noch offen) | Erstes Video mit ElevenLabs v4 (Alistair) statt seed_audio. 72 Szenen, 10:44. 3 neue 3D-Szenen (Edinburgh 2013, Kartentisch-Studio, Programmierer-Zimmer), Polaroids ohne Tilt-Shift. earshot launch-grade 0 major. |
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
- Sound-Test 17.11. (UI-Blips, Whooshes, Zähl-Sound aus SFXMint) hat Laurin ALLE abgelehnt („sehr schlecht“) -> verworfen, alte Sounds bleiben.
  Diagramm-Sound: 17.11. zuerst zip bestätigt, danach paper_slide, ENDGÜLTIG diagram_whoosh (Laurins kurzer Whoosh, 17.11.) -> bars/breakdown/flow = diagram_whoosh.
- Effekte freigegeben: phone (Push-Nachricht auf Handy), calendar (Abreißkalender). NICHT freigegeben: kinetic, ticker, spot, Lichtleck (nur auf Wunsch).
- engine/demo_mix.py: schneller Probe-Mix einzelner Szenen (Stimme + Sounds + Musik) ohne Gesamt-Mix.
- Sound-Auswahl Mixkit (17.11.): Kartenpunkt-Variante 3 „Cinematic whoosh deep impact“ = zoom_deep_impact für den Zoom von der Karte in die 3D-Animation. Zahl zählt hoch: bisherigen Sound (tick) BEHALTEN. Weitere Wahl folgt.
  Neue Sound-Quelle: Mixkit (mixkit.co/free-sound-effects/<kategorie>/, Vorschau-MP3 unter assets.mixkit.co; Lizenz: kommerziell + YouTube ok, keine Namensnennung). Laurin wählt immer selbst aus Hörproben (3 Varianten je Situation).
- Weitere Wahl 17.11.: Geld = money_clink (Mixkit „Clinking coins“, ersetzt coins), Kalenderblatt = page_turn (Mixkit „Page turn single“).
  Abgelehnt: alle 3 Mixkit-Varianten für Diagramm, Textwort, Handy-Nachricht. ERLEDIGT 17.11.: Diagramm = zip (bestätigt), Textwort = text_click, Handy = phone_notify, Kurs-Grafik = data_loading (alle von Laurin).
- Handy-Nachricht (phone) = phone_notify (Laurins eigener Notification-Sound, 17.11.). Schlagwörter = text_click (Laurins Klick). Laurin hat ein Paket mit ~1000 Effekten und schickt gezielt Sounds.
- Zeitung (news) = news_spin (Laurins Sound) statt whoosh; Blitz + Stempel bleiben (17.11.).
- Endkarte: Kommentarfeld schiebt sich mit paper_slide rein (Laurins Sound); Frage tippt sich mit Tastatursound ein (SOUNDFN endcard), restliche Endkarten-Sounds bleiben (17.11.).
- Musik an Kapitelkarten (Laurin 17.11., ENDGÜLTIG 3. Fassung): alte Musik bricht genau beim Bass-Hit der Kapitelkarte ab (Karte +0,6 s, 40 ms Blende), Karte steht ohne Musik, neuer Track beginnt 4 s nach Kapitelbeginn leise (25 %) und wird über 2,5 s normal laut (mix_full.py CARD_CUT/CARD_IN/CARD_FI). Wechsel mitten im Kapitel wie bisher.
- Earth-Zoom (Laurin 17.11.): Kartenphase A_DUR 5,1 s statt 2,6 s, Zoom gleichmäßig langsamer über die ganze Länge des neuen Risers zoom_riser (Höhepunkt beim Durchstoßen, dann zoom_deep_impact). Szenen mit earthzoom brauchen ~2,5 s mehr Platz.
- Landkarte (route) + Earth-Zoom: Pins mit pin_pop (Laurins Pop-Sound, 17.11.), Ortsnamen tippen sich mit Tastatursound ein (SOUNDFN route); zip für die Linie bleibt.
- Musik ist kanal-eigen (Laurin 17.11.): die Krimi-Bibliothek assets/music gehört nur Goldsmith, nie an andere Kanäle geben; sound-library = nur Geräusche.
- EFFEKTE PRO KANAL (Laurin 17.11., ersetzt die frühere gemeinsame Bibliothek): sound-library/ ist nur noch Goldsmiths Bibliothek. Neue Goldsmith-Sounds von Laurin dorthin + Zeile in sound-library/README.md. Andere Kanäle (Meisterwerk, Unterbau, Denkmuster …) haben eigene Effekte in ihrem Repo und binden sound-library nicht ein.
- **Update (Laurin 19.11.2026): Gemeinsame Sound-Bibliothek für alle Kanäle** – zusätzlich zu diesem Ordner dürfen alle Effekte aus `laurindesruelles-max/sound-bibliothek` genutzt werden, gefiltert nach dem Stilprofil des Kanals (README dort, `sk.py find … --channel <kanal>`). Musik bleibt kanal-eigen. Die Regel vom 17.11. („nur eigene Effekte“) gilt damit nicht mehr.
- Sound-Durchgang 17.11. abgeschlossen: Laurin hat alle Effekte angehört. Unverändert bestätigt: Kapitelkarte (braam+boom), Stempel, Vorher/Nachher, Abreißkalender, Übergänge, Polaroid-Zoom, Desktop-Grafik, Zahl zählt hoch (tick).
- Zeitleiste (timeline): je Termin text_click (derselbe Klick wie bei Schlagwörtern, Laurin 17.11.); Pin-Sound und Tastatur abgelehnt.
- Schwärzung (redact): je Balken paper_slide (Laurin 17.11.), sub_drop beim Namen bleibt.
- Textmarker in der Akte (doc) = marker_stroke / marker_stroke2 (Laurins eigene Aufnahme, 17.11.) statt highlighter.
- Kurs-Grafik (chart) = data_loading (Laurins Data-Loading-Sound) während die Linie läuft + sub_drop bei der Zahl; Herzschlag und Ticks entfernt (17.11.).
- phone-Effekt: Benachrichtigungs-Box wächst jetzt mit dem Text (vorher lief der Text unten raus).

## Musik-Feinschliff mit audiokit (Laurin 18.11.2026)
vidIQ-Auswertung 18.11.: auch bei Goldsmith läuft die Musik pro Kapitel lange gleich und bleibt vor Enthüllungen auf einem Plateau. Deshalb in engine/mix_full.py (Sounds bleiben UNVERÄNDERT – Laurins Goldsmith-Sounds sind die Qualitäts-Referenz):
- Kapitel-Tracks > 75 s springen alle ~65 s auf eine andere, spannendere Stelle desselben Tracks (Charakter bleibt).
- Vor jeder bewussten Musikpause (spec "music_rests") 3 s Crescendo (+3,5 dB) in die Stille. Mehr music_rests an echten Enthüllungen setzen.
- Endkontrolle (Lautheit, Abstand Musik/Stimme) → build/ton_bericht.txt. Abschalten: GOLDSMITH_AK=0.

## Hook-Regeln (Laurin 19.11.2026 – gilt ab dem nächsten Video)
Grundlage: Auswertung erfolgreicher Ausreißer-Videos in allen 5 Nischen (vidIQ), Hook-Studie mit über 4.000 Hooks aus Videos mit über 1 Mio. Aufrufen, Aprilynne Alters Intro-Formel. Es gibt keinen einzelnen besten Hook-Typ – aber alle erfolgreichen Hooks haben diesen Aufbau:
1. **Thema in 0–5 s gesagt UND gezeigt** – genau das, was Titel und Thumbnail versprechen; das Thumbnail-Motiv ist im ersten Bild zu sehen. Kein Datum, kein Logo, keine Vorrede als erster Satz.
2. **Offene Frage / Rätsel spätestens bei 10–15 s.** Die Antwort kommt frühestens im letzten Drittel.
3. **Konkretes Versprechen vor Hook-Ende** (was man am Ende weiß, wie viele Punkte, wer dahintersteckt).
4. **Bestes Material zuerst:** die stärkste Animation / das stärkste Bild gehört in den Hook.
5. **Kurz:** Hook-Länge siehe Kanal-Regel unten. Kontext erst danach, nicht vorne stapeln.
6. **Rehook:** Jedes Kapitel endet mit einer neuen offenen Frage.

**Prüfung vor dem Rendern** (in qa.md eintragen): Sekunde, ab der das Thema klar ist (≤ 5), Sekunde der offenen Frage (≤ 15), Versprechen ja/nein, Hook-Länge (Wörter ÷ 2,4 = Sekunden).
**Nach 48 h:** Retention bei 30 s per vidIQ (audience_retention) ins Video-Log. Ziel ≥ 70 %. Unter 50 % → beim nächsten Video den Alternativ-Typ unten nehmen.
**Goldsmith-Hook:** **Provokante Behauptung mit „you“ + Frage** („Think politicians run America? Think again.“) → Wendung („It isn't.“) → konkretes Versprechen (Countdown oder „By the end, you'll know who …“). Firma/Thema aus dem Titel und das Thumbnail-Motiv in den ersten 5 s – der Earth Zoom darf erst danach kommen. **Länge ≤ 40 s.** (Luxottica: nur noch ~33 % nach 30 s – Thema kam zu spät.)

## Video 004 – GTA 5 (21./22.11.2026)
- Auswertung (vidIQ 21.11.): Luxottica 35 Aufrufe (6 Tage), Luxury Bonfire 3, GTA 6 4 Aufrufe nach 2 Tagen → der Kanal bekommt noch kaum Impressionen. Konsequenz: Suchbegriff im Titel nach vorn („GTA 5“), Thema als erste Zeile im Thumbnail; Retention-Daten erst bei mehr Aufrufen aussagekräftig.
- Stimme: `elevenlabs_v4` mit `dialogue=[{text, voice_type: preset, voice_id: Alistair}]` funktioniert (HANDWERK: nur ElevenLabs). Higgsfield erlaubt max. 8 gleichzeitige Jobs; einzelne Jobs bleiben manchmal ewig „queued“ → nach ~3 Min. neu einreichen.
- Faktencheck VOR dem Einsprechen hat 1 echten Fehler (Sensor-Tower-Zahl ≠ „Tag 1“) und 8 Ungenauigkeiten gefunden – nie überspringen.
- KI-Bilder bei Aussagen über echte Personen (Interview, Podcast) dürfen KEINE realistischen Gesichter zeigen, sonst wirken sie wie die genannte Person → Prompts „no people, no faces“.
- Rechenzeit: 2 Kerne. Blender (FAST=1, ~470 Frames) parallel zu part2 kostet ~30 Min. extra; Szenen rendern ~1 h. Bei Bedarf 3D zuerst rendern.
- YouTube-Beschreibung max. 5.000 Bytes (nicht Zeichen) – Quellenliste kürzen. Nach draft_update mit neuer media wird publishAt zurückgesetzt → danach publishAt erneut setzen und prüfen.
- earshot: `HF_HUB_DISABLE_XET=1` nötig, sonst scheitert der Modell-Download. Ende-Stille: Bild auf Tonlänge kürzen. „Lautestes 3-s-Fenster“ zu flach → Titelkarten-Treffer anheben.
- Engine: `part2.fmt` zeigt jetzt so viele Nachkommastellen wie der Zielwert (6.66 statt 6.7); `breakdown` hat `pre`/`suf` (Prozent-Anteile statt $); setup_workdir.sh kopiert kein music_tension.mp3 mehr (gelöscht).
- Noch nicht in der Engine: die neuen Effekte aus EFFEKTE.md (Akte wird zugeschoben, Wand wächst, Lampe schwenkt) – nur Stilprobe vorhanden. Nächster Schritt: in part2/effects einbauen.
