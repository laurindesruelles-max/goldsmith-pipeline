# Goldsmith – Lernbuch (wird bei JEDEM Video gelesen und ergänzt)

Ziel: Jedes Video ist besser als das letzte – Schnitt, Spannung, Sound, Thumbnail.

## Feste Regeln aus Laurins Feedback
- Keine 3D-Figuren/Mannequins, keine reine Diashow. Viele Bewegungsgrafiken, Effekte auf jedem Element.
- Daten und Orte immer als Schreibmaschinentext mit mechanischem Tastatursound (assets/sfx/key0-7, Lautstärke Faktor 0.75 – vorher zu leise/zu laut).
- Musik muss spannend sein (ElevenLabs-Tracks, nie selbst synthetisiert). Pro Kapitel passender Track (spec "music").
- Spannung braucht Pausen: nach jeder großen Enthüllung 0,8–1,5 s Stille (spec "beats"), Musik taucht ab, dann Hit.
- Thumbnail: Hero-Stil, EIN großes Motiv, 2 Zeilen, Zahl oder Frage zum Geld des Zuschauers. Text auf Preisschild mittig (tag xy "auto").

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
| 002 | Why Luxury Brands Burn Their Own Clothes | 16.11.2026 | Hero „THEY BURNED £28.6 MILLION“ | (noch offen) | Erstes Video mit allen Effekten, Kapitelmusik und Pausen. Länge ~8 Min (kürzer als 001). Thumbnail-Heroes mit Handtaschen ähneln echten Designermodellen (Birkin/Chanel) → solche Motive meiden. |
| 001 | The Company That Secretly Owns Your Glasses | 15.11.2026 | Hero A „YOU PAY 20X MORE?“ | (noch offen) | Pilot. Musik war nur 1 Track in Schleife; keine Pausen. Ab 002: Kapitel-Musik + beats. |
