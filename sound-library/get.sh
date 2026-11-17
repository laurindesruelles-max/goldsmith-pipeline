#!/bin/sh
# Lädt Laurins gemeinsame Sound-Bibliothek in einen Ordner.  Usage: sh get.sh <zielordner>
set -e
DEST="${1:?Zielordner angeben}"; mkdir -p "$DEST"
TMP=$(mktemp -d)
git clone -q --depth 1 --filter=blob:none --sparse https://github.com/laurindesruelles-max/goldsmith-pipeline "$TMP/r"
(cd "$TMP/r" && git sparse-checkout set sound-library >/dev/null)
cp "$TMP"/r/sound-library/*.wav "$DEST/"
echo "Sound-Bibliothek: $(ls "$TMP"/r/sound-library/*.wav | wc -l) Sounds nach $DEST"
rm -rf "$TMP"
