# Geräusch-Bibliothek (assets/sfx)

Alle neuen Geräusche: CC0 (frei, auch kommerziell, keine Quellenangabe nötig) von SFXMint (sfxmint.com), geladen über Hugging Face (flreey/sfxmint-cc0-sound-effects, Ordner sample) bzw. die SFXMint-API. Jedes Geräusch wurde auf Rauschen geprüft, gesäubert (Hochpass, Stille abgeschnitten) und lautheitsnormalisiert (Effekte −20 LUFS, Atmo −28 LUFS).

**Regel (Laurin 16.11.2026): Kein Rauschen/Wind als Teppich. Nur Geräusche, die man im Bild sieht** – in Blender per `D.sound(name, frame, objekt, ...)` an Objekte hängen (drive/walk machen das automatisch). Atmo (`amb_*`) nur sehr leise und nur, wenn sie zur Szene passt.

Neue Geräusche: Hugging-Face-Sample (frei, unbegrenzt) → sonst SFXMint-API mit Laurins Schlüssel (5/Tag, Umgebungsvariable `SFXMINT_KEY`, NIE ins Repo schreiben) → Laurin lädt im Browser herunter. Higgsfield (mirelo) nur als letzte Wahl.

**Regel (Laurin 17.11.2026): Bei jedem Sound, der nicht CC0 ist, die Herkunft sichern** – Link, Kanal/Seite, Lizenzangabe des Uploaders, Datum und Originaldatei in `_herkunft/<name>.md` + Originaldatei ablegen.

| Name | Quelle (SFXMint-ID) | Inhalt |
|---|---|---|
| shutter | YouTube „5 Camera Shutter Sound Effects (No Copyright)“ von Sound Effects Treasure, youtu.be/R24UqkKj90w, Klick 3 von 5 – Nachweis in _herkunft/shutter.md | mechanischer Kamera-Auslöser – Beweisfoto, Polaroid, Endcard (von Laurin gewählt) |
| money_clink | Mixkit „Clinking coins“ (Mixkit-Lizenz) | Münzen klimpern – Geld (von Laurin gewählt) |
| page_turn | Mixkit „Page turn single“ (Mixkit-Lizenz) | Seite umblättern – Kalenderblatt (von Laurin gewählt) |
| zoom_deep_impact | Mixkit „Cinematic whoosh deep impact“ (Mixkit Sound Effects Free License: kommerziell, keine Namensnennung) | tiefer Whoosh mit Treffer – Earth Zoom: Karte → 3D (von Laurin gewählt) |
| car_pass | car-pass-by-01 | Auto fährt vorbei |
| car_pass_2 | car-pass-by-05 | Auto fährt vorbei (Variante) |
| car_arrive | car-slowing-to-a-stop-04 | Auto rollt heran und hält |
| car_arrive_2 | car-slowing-to-a-stop-01 | Auto hält (Variante, etwas mehr Umgebung) |
| car_door | car-door-opening-and-closing-01 | Autotür auf und zu |
| footsteps_street | footsteps-concrete-03 | Dark footsteps on concrete for walking characters and city scenes in games and videos. |
| footsteps_stairs | footsteps-stairs-36 | Footsteps on stairs for climbing stairs and house scenes in games and videos. |
| footsteps_heels | footsteps-heels-36 | High heels footsteps for characters walking, or for offices and hallways, in videos and games. |
| neon_buzz | fire-electric-hum-39 | An electric hum sound for machines and power rooms, or for sci-fi backgrounds, in games and videos. |
| clock_tick | metronome-ticking-01 | A mechanical pendulum metronome ticking evenly at a moderate pace. |
| filing_metal | steel-spike-scrape-01 | A steel spike scrape sound for spike traps and blades scraping metal in games and videos. |
| hammer | hammer-01 | A hammer sound for building and repair, or for crafting games, in games and videos. |
| door_open | door-open-01 | A door opening sound for entering rooms and scene transitions in games and videos. |
| door_close | door-close-01 | A door closing sound for characters leaving rooms and scene transitions in games and videos. |
| door_creak | door-creak-01 | A door creak sound for opening doors and suspense scenes in games and videos. |
| door_knock | door-knock-01 | A dark door knock sound for someone at the door and suspense scenes in games, videos and apps. |
| door_lock | door-lock-01 | A bright door lock sound for locking and unlocking doors, or for secure actions, in games and apps. |
| door_bell | door-doorbell-01 | A bright doorbell sound for visitors arriving and smart home alerts in apps, games and videos. |
| service_bell | service-bell-01 | A soft service bell, for calm UI. |
| phone_ring | office-ringtone-01 | A phone ringtone sound for incoming calls and phone scenes in apps, videos and games. |
| elevator_ding | office-elevator-08 | An elevator ding sound for elevators and arrival cues in videos, games and apps. |
| camera_click | office-camera-08 | A bright camera shutter sound for taking photos and screenshots in apps and videos. |
| amb_factory | factory-machinery-ambience-01 | A factory machinery ambience sound for industrial levels and workshop scenes in games and videos. |
| amb_night | night-ambience-01 | A night ambience sound for night scenes and sleep apps in videos, games and apps. |
| amb_lab | laboratory-ambience-01 | A laboratory ambience sound for science scenes and labs, or for sci-fi games, in games and videos. |
| amb_river | river-ambience-01 | A river ambience sound for nature backgrounds and riverbank scenes in videos, games and apps. |
| amb_rain | ambience-rain-03 | An airy rain sound for calm night backgrounds and rainy weather in videos and games. |
| amb_fire | gentle-fire-crackling-01 | Gentle fire crackling, about 6 seconds long. Use it for campfires, hearths and cozy background scenes in games and videos. |
| amb_market | busy-market-crowd-murmur-walla-01 | A crowd murmur sound for busy public backgrounds and restaurant scenes in videos and games. |
| crowd_hushed | daily-20260923-hushed-crowd-walla-short | A hushed crowd murmuring indistinctly in the background, about 4.7 seconds long. Use it for waiting rooms, lobbies and quiet audience scenes. |
| crowd_applause | crowd-applause-01 | An applause sound for performances and awards, or for celebrations, in videos, games and apps. |
| crowd_angry | angry-crowd-01 | An angry crowd sound for protests and riots, or for hostile crowds, in games and videos. |
| coins_table | coin-dropped-on-wooden-table-01 | A coin dropped on table sound for tips and payments, or for tabletop scenes, in videos, games and apps. |
| banknote_counter | empty-banknote-counter-01 | A money counting sound for banks and shops, or for money games, in games, videos and apps. |
| keys_jingle | keys-jingling-01 | A small ring of metal house keys jingling briefly in one hand. |
| lighter | lighter-flick-01 | A lighter flick sound for smoking scenes and lighting a fire in videos and games. |
| match_strike | match-strike-01 | One wooden match struck along a matchbox, igniting with a brief flare and settling into a small flame. |
| marker_write | marker-writing-01 | A marker writing sound for classroom scenes and drawing apps in videos, apps and games. |
| paper_flip | paper-fabric-card-flip-06 | A bright card flip sound for card games and flip animations in games and apps. |
| scroll_unroll | scroll-unroll-01 | A scroll unroll sound for quests and maps, or for letters, in games. |
| iron_gate | iron-gate-01 | A metal gate rattling, for fences. |
| step_metal | boot-step-on-metal-plate-01 | A single footstep sound for single steps and animation timing in games and videos. |
| subway_train | subway-train-01 | A subway train sound for commutes and stations, or for city scenes, in games and videos. |
| bus_engine | bus-engine-01 | A bus engine sound for cities and bus stops, or for travel, in games and videos. |
| jet_engine | jet-engine-01 | A jet engine sound for airports and aircraft, or for engines, in games and videos. |
| plane_cabin | airplane-cabin-ambience-01 | A short airplane passenger cabin background with steady engine rumble and ventilation. |
| harbor_ships | owner-continuous-20260922-ocean-arriving-ships-composite | Rolling ocean surf with a large ship horn sounding midway, about 12 seconds long. Use it for harbor arrivals, coastal scenes and travel videos. |
| glass_shatter | glass-shatter-01 | A bright glass shattering sound for breaking windows and action scenes in games and videos. |
| body_fall | body-fall-01 | A body fall sound for knockouts and falls, or for fight scenes, in games and videos. |
| car_gravel | car-on-gravel-01 | A car on gravel sound for driveway arrivals and rural roads in videos and games. |
| lever | mechanical-lever-36 | A lever pull sound for puzzles and mechanisms, or for dungeon switches, in games. |
| machine_engine | mechanical-engine-39 | An engine running sound for vehicles and machinery backgrounds in games and videos. |
| cash_drop | sack-drop-01 | A sack drop sound for farms and storage, or for loading, in games. |
| bell_toll | temple-bell-01 | A temple bell sound for meditation and ceremonies, or for calm apps, in apps, videos and games. |

Ältere Effekt-Sounds (stamp, slap, braam, boom, riser, tick, pin, paper, whoosh, …) und die Tastatursounds key0–7 (extern, setup_workdir.sh) bleiben unverändert.
