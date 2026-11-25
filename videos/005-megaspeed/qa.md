# Prüfbericht – 005-megaspeed (2026-11-25)

## 1. Technik (automatisch, engine/qa.py)
- [x] OK: Länge 12:29 (Minimum 8:00)
- [x] OK: Bild 1920x1080
- [x] OK: Tonspur vorhanden
- [x] OK: Lautheit -14.0 LUFS (Ziel -14 ±2,5)
- [x] OK: Spitzenpegel -1.0 dBFS (max. −0,5)
- [x] OK: Schwarzbilder mitten im Video: keine
- [x] OK: Standbild-Stellen (≥4 s ohne Bewegung): 0 
- [x] OK: Dateigröße 286 MB (Info – Upload-Kopie muss < 299 MB sein)
- [x] Kontaktbogen `qa_frames.jpg` angesehen. Gefunden und behoben: Schlagwörter (pop) lagen über der Schreibmaschinen-Box (Szenen 3, 9, 10, 11, 20, 32, 39, 41, 46, 49, 59, 65, 66) → Engine: pop wandert nach oben, wenn eine typed-Box sichtbar ist; Szenen neu gerendert. Doppelte Kapitelkarte (Titel + Kapitel 1 in 3 s) → Kapitel-1-Karte entfernt.
- [x] Upload-Kopie: −14,0 LUFS, −1,0 dBTP (Gain +1,6 dB + Limiter), 2850 kbit/s, 286 MB.


## 1b. Ton (doku-ohren)
- earshot critique (Upload-Fassung) gegen doku_profil.json: **launch-grade, 22/23 Messwerte im Rahmen, 0 critical, 0 major** (1 minor: fast mono). Erste Messung hatte 1 major (lautestes 3-s-Fenster nur 1,9 LU über Mittel) → mix_full.py hebt die erste Kapitelkarte an; danach 0 major.
- earshot realness: 0 von 188 Fenstern klingen synthetisch.
- Gemini (gemini-3-flash-preview) hörte 0:00–2:00: **PREMIUM** – Stimme immer klar über der Musik, Pause bei „It isn't.“ stark; Kritik: text_click-Folge bei 1:12–1:20 etwas laut, Pin-Sound „stock“. Ausschnitt 6:40–8:10: **OK** – Stempel „RE-ENTRY BARRED“ und Tastatur etwas laut/stock, Verschlüsselungs-Sound generisch. → Laurins abgenommene Sounds nicht eigenmächtig geändert, Frage an Laurin.
- Freesound-Suche (Server-Brummen): nur Rausch-Teppiche → kein neuer Sound.
- sk.py check: brach ab (earshot sheet braucht matplotlib) – stattdessen critique + Gemini.
- Stimme: ElevenLabs v4 (Alistair), 71 Dateien; kein ASR-Abgleich möglich (kein Parakeet in dieser Umgebung), Stichproben über Gemini-Hörprobe ohne Auffälligkeiten.

## 0. Bild-Drehbuch + Hook
- [x] `python3 engine/bilddrehbuch.py videos/005-megaspeed/bilddrehbuch.json --kanal goldsmith` → **OK, 0 Fehler** (220 Einstellungen, ~18,7 Bild-Ereignisse/Min; nur Warnungen).
- Hinweis: „Akte wird zugeschoben“, „Wand wächst“ und „Lampe schwenkt“ sind im Drehbuch als Bild-Idee benannt, in der Engine aber noch nicht als eigene Effekte gebaut – umgesetzt über Kapitelkarte, Rückzoom-Bild (67) und `flicker`.
- Hook: Thema (Megaspeed + Nvidia-Chips) in Satz 1 (0–5 s) gesagt und gezeigt; Neugier-Frage ab 0 s; offene Frage „where they went, who rented them, who knew“ ~1:00; Versprechen in 3 Teilen (Szene 7). Hook ≈ 80 s – länger als die 40-s-Regel (Kaltstart Johor + Eskalationstreppe nach Wissenswert-Vorbild).

## 2. Fakten – unabhängiger Faktencheck VOR dem Einsprechen (separater Agent, 47 Web-Abrufe)
| Szene | Aussage | Stimmt? | Korrektur |
|---|---|---|---|
| 1 | $7,5 Mrd. (The Information) | teilweise | gilt für Megaspeed **und** Tochter Speedmatrix |
| 2 | Ende 2024 Beamter in Johor, Chips in Kartons | teilweise | NYT: **September 2024**, „according to The New York Times“ |
| 14 | $33 Mio. → ~$3 Mrd. „laut The Edge“ | teilweise | Quelle: Firmenunterlagen via Reuters |
| 18 | Vermieten „nach aktuellen Regeln legal“ | **nein (veraltet)** | BIS-Regel 16.11.2026 → „was, until this month, legal“; neue Szene 51 |
| 22 | $4,8 Mrd. | ja | Zeitraum Juni 2024–Feb. 2026 ergänzt |
| 24 | Route 2 „illegal“ | teilweise | „which may violate U.S. export controls“ |
| 27 | Schwester Gründungsaktionärin | ja | „no public evidence that Alice Huang directed those purchases“ |
| 28 | Megaspeed-Zitat | unbelegt | ersetzt durch „legitimate and lawful business“ |
| 34 | Nvidia „small commercial cloud“ | ja | „found no evidence of diversion“ ergänzt |
| 41 | Singapur Feb. 2026 | teilweise | Einreiseverbot (MHA) ergänzt |
| 43/44 | Memo, DOJ | ja | Balance: CNN – US-Geheimdienste uneins; AG Todd Blanche |
| 50/52 | „Five days later“ / „that same day“ | **nein** | „Four days later“ (16.11.); Umsatz „the next day“ |
| 55 | Alibaba-Firma | ja | Apex, Singapur-Tochter von Alibaba; Alibaba: „erroneous“ |
| 58 | Bessent „had the pen“ | teilweise | „Commerce **has** the pen“, vier Behörden |
| 59 | WSJ „decisions“ | teilweise | „activities“, „who has not been convicted“, ohne Namen |
| 62 | „no evidence of illicit transfers“ | teilweise | Nvidia-Wortlaut „no evidence of diversion“ |
| 63 | „Singapur fand keine ausreichenden Beweise“ | **nein (irreführend)** | nur zu Alice Huang; Ermittlung gegen Megaspeed läuft |
| 65/66 | Gesetz / Anhörung | ja | „In January“; Senate Banking ergänzt |
| 67 | „start of a map“ | Risiko | „raised a question investigators are still trying to answer“ |
- [x] Jede Zahl, jedes Datum, jeder Name, jedes Zitat geprüft; alles mit „nein“/„unbelegt“ vor der Vertonung geändert.

## 3. Recht (keine Rechtsberatung – Sorgfaltsprüfung)
- [x] Unschuldsvermutung: Spionage-Vorwurf immer zugeschrieben, Gegenstimmen (China, CNN, DOJ) und „not charged“ (4, 44, 62); Entity List = „significant risk“, keine Feststellung (54); Megaspeed-Dementis (25, 28, 60); Beschreibung mit Hinweis.
- [x] Angeklagter in Singapur nicht namentlich genannt, „has not been convicted“.
- [x] Privates nur, was Jensen Huang selbst öffentlich geschrieben hat (Brief 8.11.); weitere Affären-Berichte weggelassen.
- [x] Keine echten Fotos realer Personen, keine KI-Gesichter (Silhouetten, von hinten); 3D-Figuren gesichtslos, „RECONSTRUCTION“ beschriftet.
- [x] Keine Logos (auch nicht im Thumbnail); „Nvidia“ nur als Text. Thumbnail stellt eine Frage, keine Behauptung.

## 4. Lizenzen
| Material | Quelle | Lizenz |
|---|---|---|
| Stimme | ElevenLabs v4 über Higgsfield (Alistair) | Higgsfield-Nutzungsrechte |
| Szenen- und Hero-Bilder | Higgsfield gpt_image_2_6 | Higgsfield-Nutzungsrechte |
| 3D (aerial_johor, datahall, cargo_dock, taipei_bar) | Blender, eigene Modelle + Poly Haven | CC0 |
| Musik | assets/music (Goldsmith-Bibliothek) | eigen |
| Sounds | sound-library / assets/sfx | CC0 / Laurins Nachweise |
| Pixabay-Videos 198477, 338956, 24136, 47215, 377885, 87884, 23759, 380334, 152728, 338955, 191518, 166285, 239278, 328740 | pixabay.com | Pixabay Content License |
- KI-Bilder wirken teils wie echte Orte (Singapur, Shanghai, Capitol) → beim Upload „Veränderte oder synthetische Inhalte: Ja“ empfohlen.

## 5. Kosten
Higgsfield ≈ 77 Credits (Stimme ElevenLabs v4 ≈ 52, 96 Bilder + 3 Hero ≈ 25) – über der 45er-Marke aus HANDWERK.md, weil ElevenLabs Pflicht ist und das Skript 1.614 Wörter hat. Guthaben vorher 2.527.
