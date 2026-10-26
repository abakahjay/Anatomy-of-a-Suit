#!/usr/bin/env bash
# Turns one film into the site's frame sequences.
# Usage: tools/import-film.sh film.mp4 [film-portrait.mp4]
# Writes 535 frames to public/frames/desktop and public/frames/mobile (centre crop of the film unless a portrait film is given).
set -euo pipefail
cd "$(dirname "$0")/.."
FILM=$1; PORTRAIT=${2:-}
TOTAL=535

sample() { # input outdir filter
  local dur; dur=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$1")
  rm -rf "$2"; mkdir -p "$2"
  ffmpeg -v error -y -i "$1" -vf "$3,fps=${TOTAL}/${dur}" -frames:v $TOTAL -q:v 4 "$2/%04d.jpg"
  echo "$2: $(ls "$2" | wc -l) frames, $(du -sh "$2" | cut -f1)"
}

sample "$FILM" public/frames/desktop "scale=1600:900:force_original_aspect_ratio=increase,crop=1600:900"
if [ -n "$PORTRAIT" ]; then
  sample "$PORTRAIT" public/frames/mobile "scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280"
else
  sample "$FILM" public/frames/mobile "crop=ih*9/16:ih,scale=720:1280"
fi
