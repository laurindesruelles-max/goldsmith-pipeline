#!/bin/sh
# Usage: sh engine/setup_workdir.sh videos/NNN-slug /home/claude/work
# Baut die Ordnerstruktur, die die Engine erwartet:
#   WORK/scenes.json  WORK/audio/N.wav  WORK/img/N.png
#   WORK/v3/{case.py,part2.py,mix_full.py,timing.json,spec.json,a/,sfx/,music_tension.mp3,build/}
set -e
REPO=$(cd "$(dirname "$0")/.." && pwd); VID="$REPO/$1"; WORK="$2"
mkdir -p "$WORK/audio" "$WORK/img" "$WORK/v3/a" "$WORK/v3/build" ~/.fonts
cp "$REPO"/assets/fonts/* ~/.fonts/
cp "$REPO"/engine/*.py "$WORK/v3/"; cp -r "$REPO/assets/sfx" "$WORK/v3/sfx"
cp "$REPO"/sound-library/*.wav "$WORK/v3/sfx/"   # Goldsmith-Sound-Bibliothek (Laurins Goldsmith-Sounds)
mkdir -p "$WORK/v3/diorama" "$WORK/v3/dio"; cp -r "$REPO"/engine/diorama/* "$WORK/v3/diorama/"
python3 -c "import bpy" 2>/dev/null || pip install bpy --break-system-packages -q   # Blender für 3D-Dioramen
# Tastatursounds liegen NICHT im (öffentlichen) Repo, sondern in Laurins Higgsfield-Speicher:
if [ ! -f "$WORK/v3/sfx/key0.wav" ]; then
  curl -sSfL -o /tmp/goldsmith_keys.zip "https://d2ol7oe51mr4n9.cloudfront.net/user_3LhrXzDQGZeDXCNfJbMSIhJMEcn/a97d9544-3788-456e-802a-03b6847d4f8c.zip" && (cd "$WORK/v3/sfx" && unzip -oq /tmp/goldsmith_keys.zip) || echo "WARNUNG: Tastatursounds nicht ladbar (Domain d2ol7oe51mr4n9.cloudfront.net freigeben)"
fi
cp "$REPO"/assets/img/*.png "$WORK/v3/a/"; mkdir -p "$WORK/v3/music"; cp "$REPO"/assets/music/*.mp3 "$WORK/v3/music/"
cp "$VID/scenes.json" "$WORK/"
[ -f "$VID/spec.json" ] && cp "$VID/spec.json" "$WORK/v3/"
[ -f "$VID/timing.json" ] && cp "$VID/timing.json" "$WORK/v3/"
# Ton-Werkzeug audiokit (18.11.2026): Sounds aufräumen, Musik nach Spannungskurve, Endkontrolle.
# Gemeinsam sind nur die Regeln – Sounds und Musik bleiben kanal-eigen. Repo: laurindesruelles-max/sound-mediathek
AK="${AUDIOKIT:-/home/claude/audiokit}"
if [ ! -f "$AK/adapter.py" ] || [ -n "$AK_UPDATE" ]; then
  AKT=$(mktemp -d); git clone -q --depth 1 --filter=blob:none --sparse https://github.com/laurindesruelles-max/sound-mediathek "$AKT/r" && git -C "$AKT/r" sparse-checkout set audiokit && mkdir -p "$AK" && cp "$AKT"/r/audiokit/*.py "$AKT"/r/audiokit/*.json "$AK"/ && echo "audiokit bereit: $AK"; rm -rf "$AKT"
fi
# 2D-Motion-Graphics (Remotion, engine/motion): einmal Node-Pakete installieren
MO="$(dirname "$0")/motion"; [ -d "$MO/node_modules" ] || (cd "$MO" && npm install --silent >/dev/null 2>&1 && echo "motion bereit")
echo "Workdir bereit: $WORK  (Audio nach audio/, Bilder nach img/, dann in v3/: FIRST_SCENE=1 python3 part2.py meta)"
