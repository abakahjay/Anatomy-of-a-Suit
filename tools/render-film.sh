#!/usr/bin/env bash
# Renders the Blender film into the site's frame folders.
# Usage: BLENDER=/path/to/blender.exe tools/render-film.sh
# Renders in batches of single frames (the 5.4 alpha crashes on full animation renders) and skips frames already done,
# so it can be stopped and restarted.
set -euo pipefail
cd "$(dirname "$0")/.."
B=${BLENDER:-blender}
OUT="$(pwd -W 2>/dev/null || pwd)/build/film"
mkdir -p build/film
TOTAL=535; BATCH=60
todo=()
for f in $(seq 1 $TOTAL); do [ -f "build/film/$(printf %04d $f).jpg" ] || todo+=($f); done
for ((i = 0; i < ${#todo[@]}; i += BATCH)); do
  list=$(IFS=,; echo "${todo[*]:i:BATCH}")
  "$B" -b --factory-startup --gpu-backend opengl --python tools/suit_film.py -- "$OUT" "$list" 1600 > /dev/null 2>&1 || true
  echo "rendered $(ls build/film | wc -l)/$TOTAL"
done
n=$(ls build/film | wc -l)
[ "$n" -eq $TOTAL ] || { echo "only $n frames, run again"; exit 1; }
rm -rf public/frames/desktop public/frames/mobile && mkdir -p public/frames/desktop public/frames/mobile
cp build/film/*.jpg public/frames/desktop/
# phones: a portrait crop around the figure (the camera shifts him to 59% across)
ffmpeg -v error -y -i build/film/%04d.jpg -vf "crop=506:900:691:0,scale=720:1280:flags=lanczos" -q:v 4 public/frames/mobile/%04d.jpg
echo "desktop $(ls public/frames/desktop | wc -l), mobile $(ls public/frames/mobile | wc -l)"
