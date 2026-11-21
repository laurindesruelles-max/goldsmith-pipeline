# Prüfbericht – 004-gta5-money-machine (2026-11-22)

## 1. Technik (automatisch, engine/qa.py)
- [x] OK: Länge 10:44 (Minimum 8:00)
- [x] OK: Bild 1920x1080
- [x] OK: Tonspur vorhanden
- [x] OK: Lautheit -14.1 LUFS (Ziel -14 ±2,5)
- [x] OK: Spitzenpegel -1.0 dBFS (max. −0,5)
- [x] OK: Schwarzbilder mitten im Video: keine
- [x] OK: Standbild-Stellen (≥4 s ohne Bewegung): 0 
- [x] OK: Dateigröße 270 MB (Info – Upload-Kopie muss < 299 MB sein)
- [x] Kontaktbogen angesehen. Gefunden und behoben: KI-Bilder mit realistisch wirkenden Männergesichtern in Szene 31 (Magazin beim Sarwar-Zitat) und 32 (Podcast beim Ex-Rockstar-Mitarbeiter) könnten als echte Personen gelesen werden → ohne Personen neu erzeugt, Szenen neu gerendert.
- [x] Master-Spitze 0,0 dBTP → Upload-Kopie: Gain auf −14,1 LUFS + Limiter (−1,0 dBFS). Ende: 0,4 s Stille hinter dem Ton → Bild auf Tonlänge gekürzt.

## 2. Fakten (unabhängiger Faktencheck durch separaten Agenten)
Recherche-Agent (Primärquellen) + unabhängiger Faktencheck-Agent VOR dem Einsprechen. Ergebnis: ein echter Fehler, mehrere Formulierungen entschärft – alles vor der Vertonung korrigiert.
| Szene | Aussage | Stimmt? | Korrektur |
|---|---|---|---|
| 64 | GTA VI „$2,36 Mrd. am ersten Tag, fast 3× GTA V“ | nein (irreführend) | Sensor-Tower-Schätzung inkl. Vorbestellungen, nur digital; Vergleich gestrichen, „Take-Two hasn't confirmed“ |
| 45 | MarketWatch $6 Mrd., „most profitable“ | teilweise | „brought in more than $6B … by that estimate more than any film“ |
| 46/47 | Leak $500 Mio./Jahr, $1,3 Mio./Tag | unbestätigt | „hackers claimed …“, „according to reports …“, „on average“, „Rockstar has not confirmed“ |
| 58/68 | 78 % / 81 % wiederkehrende Ausgaben | ja, aber Take-Two gesamt | „across all its games“ ergänzt |
| 43 | GTA+ „monthly bill“ | irreführend | „optional monthly membership“ |
| 42 | GTA+ $5,99 | ja (zum Start) | „launched at“ |
| 40 | „Some players bought it 2–3 times“ | unbelegt | „Many fans paid for it again on new hardware“ |
| 4 | „Most publishers would have released three sequels“ | Meinung | „Many franchises would have seen several sequels“ |
| 9, 13, 27, 38 | Studios / Mitternachtsverkauf / 2020-Statement / „third time“ | ungenau | präzisiert (Rockstar North led, thousands of stores, early 2020, third generation) |
| 61 | Zelnick „four words“ | nein (3 Wörter) | „put it simply“ |
Alle übrigen Zahlen/Daten bestätigt (Take-Two PR 2013, Guinness, Scotsman/GameSpot, VGC, Engadget, IBTimes, Kotaku, PC Gamer, Business Wire, GamesBeat, Push Square).
- [x] Jede Zahl, jedes Datum, jeder Name, jedes Zitat geprüft; alles mit „nein“/„unbelegt“ wurde geändert oder gestrichen

## 3. Recht (keine Rechtsberatung – Sorgfaltsprüfung)
- [x] Äußerungsrecht: Tatsachen nur mit Beleg; Vorwürfe/laufende Verfahren als „Vorwurf“/„laut …“; Urteile korrekt (Gericht, Jahr); Meinung als Meinung erkennbar; keine Beleidigung, keine Spekulation über Privates
- [x] Personen (einziges echtes Foto: Strauss Zelnick, Person des öffentlichen Lebens, CC BY 2.0, unverändert, sachlicher Kontext): keine echten Fotos, keine realistischen KI-Gesichter realer Personen, keine Privatpersonen identifizierbar
- [x] Marken: keine Logos/Markenzeichen im Bild oder Thumbnail; Markennamen nur beschreibend; Hinweis „not affiliated/endorsed“ in der Beschreibung
- [x] Titel und Thumbnail versprechen nichts, was das Video nicht belegt (kein irreführender Vorwurf)

## 4. Lizenzen (Protokoll)
| Material | Quelle | Lizenz |
|---|---|---|
| Sprecherstimme | ElevenLabs v4 über Higgsfield (Preset Alistair) | Higgsfield-Abo (kommerzielle Nutzung laut Plan) |
| KI-Bilder / Thumbnail | Higgsfield gpt_image | Higgsfield-Abo |
| Musik | assets/music (ElevenLabs über Higgsfield) | Higgsfield-Abo |
| Geräusche | assets/sfx (SOUNDS.md) – SFXMint | CC0 |
| Geräusche | sound-library (README.md) – Laurins Effekt-Sammlung / No-Copyright-Effekte | von Laurin freigegeben |
| 3D-Texturen/Modelle | Poly Haven | CC0 |
| Schriften | Anton, Special Elite, Playfair Display, Inter | SIL OFL / Apache |
| Foto Strauss Zelnick | Wikimedia Commons, Christopher Michel | CC BY 2.0 (Nachweis im Bild + Beschreibung) |
- [x] Kein fremdes Material (Filmausschnitte, Fotos, Musik) außer den oben gelisteten Quellen

## 5. YouTube
- [x] Realistisch wirkende KI-Bilder (Edinburgh-Luftbild, Launch-Nacht, Börse) → echter Orte/Ereignisse → beim Upload „Veränderte oder synthetische Inhalte: Ja“ setzen (Laurin im Studio, falls die API es nicht kann)
- [x] Beschreibung (4.845 Bytes, YouTube-Limit 5.000): Quellenliste, Kapitel, Marken-Hinweis; keine < oder > Zeichen
- [x] Werbefreundlich: keine Gewaltbilder, keine Schimpfwörter, keine reißerischen Schock-Thumbnails mit Verletzungen

## Ergebnis: TECHNIK OK · Fakten/Recht/Lizenzen: oben abhaken, erst dann Laurin zur Freigabe schicken

## 6. Ton (doku-ohren)
- earshot critique (Upload-Kopie, Profil fern/Simplicissimus/Netflix): **launch-grade, 22/23, 0 critical, 0 major**. Vorher 2 major (lautestes 3-s-Fenster nur +2,4 LU → Titelkarte +4,6 dB angehoben; 0,4 s Stille am Ende → gekürzt). Rest: minor „fast mono“ (Musik/SFX-Bibliothek ist mono-lastig).
- Gemini (gemini-3.8-flash, erste 2 Min.): 5/10 (Gemini gibt auch fern nur 5/10). Fundstellen: Tastatur- und Zähl-Ticks hell (2–5 kHz), Glitch-Übergang bei 1:00 „preset-artig“, Spitze über 0 dBTP (in Upload-Kopie behoben). Gemeldete „Wiederholung des Anfangs ab 1:29“ geprüft: falsch – dort beginnt Szene 11 mit neuem Text. Laurins abgenommene Goldsmith-Sounds nicht eigenmächtig geändert; Hinweise an Laurin weitergegeben.
- mix_full-Endkontrolle: „Musik unter Stimme −1,7 dB“ misst die Rohspuren vor Sidechain/0,42-Gain (wie bei 003) – kein Befund im fertigen Mix.

## 7. Hook (Prüfung vor dem Rendern)
- Thema (GTA 5 + Geld) bei 0–4 s gesagt und gezeigt; offene Frage bei ~0:30; Versprechen („three tricks“) bei ~0:42; Hook-Länge 51 s (über der 40-s-Regel, Titelkarte bei 0:51).
