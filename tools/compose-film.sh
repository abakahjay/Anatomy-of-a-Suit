#!/usr/bin/env bash
# Joins real footage and the Blender suit build into one 535-frame film, for desktop and phone.
#   0 street at night (footage)  ->  1-4 shirt, waistcoat, canvas, full cut (Blender, build/film 52-348)
#   5 buttoning the jacket  ->  6 three men on the steps  ->  7 cufflinks close-up (footage)
# Footage is from Pexels (Pexels License), see footage/CREDITS.txt. Needs build/film from tools/render-film.sh.
set -euo pipefail
cd "$(dirname "$0")/.."
FPS=24; X=0.4; TOTAL=535
TMP=build/compose; rm -rf "$TMP"; mkdir -p "$TMP"
# the same dark green noir as the Blender stage
GRADE="eq=contrast=1.15:brightness=-0.09:saturation=0.5,colorbalance=rs=-0.04:gs=0.015:bs=-0.03:rm=-0.03:gm=0.01:bm=-0.01,vignette=angle=PI/4"

build() { # mode W H
  local mode=$1 W=$2 H=$3 cover="scale=$2:$3:force_original_aspect_ratio=increase,crop=$2:$3"
  local cuff blend_crop
  if [ "$mode" = mobile ]; then cuff="$cover"; blend_crop="crop=506:900:691:0,scale=$W:$H:flags=lanczos"
  else cuff="crop=1080:608:0:420,scale=$W:$H:flags=lanczos"; blend_crop="scale=$W:$H"; fi
  clip() { ffmpeg -v error -y -ss "$2" -t "$3" -i "footage/$1.mp4" -an -vf "$4,fps=$FPS,$GRADE,format=yuv420p" -c:v libx264 -crf 12 -preset veryfast "$TMP/$mode-$5.mp4"; }
  clip walk-night 4.0 2.7 "$cover" a
  ffmpeg -v error -y -framerate $FPS -start_number 52 -i build/film/%04d.jpg -frames:v 297 -vf "$blend_crop,format=yuv420p" -c:v libx264 -crf 12 -preset veryfast "$TMP/$mode-b.mp4"
  clip buttoning 1.0 2.6 "$cover" c
  clip three-men 2.5 3.31 "$cover" d
  clip cufflinks 0.5 2.95 "$cuff" e
  # dissolves land on the chapter boundaries (frames 60, 340, 400, 470)
  ffmpeg -v error -y -i "$TMP/$mode-a.mp4" -i "$TMP/$mode-b.mp4" -i "$TMP/$mode-c.mp4" -i "$TMP/$mode-d.mp4" -i "$TMP/$mode-e.mp4" -filter_complex \
    "[0][1]xfade=transition=fade:duration=$X:offset=2.3[ab];[ab][2]xfade=transition=fade:duration=$X:offset=14.275[ac];[ac][3]xfade=transition=fadeblack:duration=$X:offset=16.47[ad];[ad][4]xfade=transition=fade:duration=$X:offset=19.38,fade=t=out:st=21.7:d=0.6[v]" \
    -map "[v]" -c:v libx264 -crf 14 -preset veryfast "$TMP/$mode-film.mp4"
  local dur; dur=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$TMP/$mode-film.mp4")
  rm -rf "frames/$mode"; mkdir -p "frames/$mode"
  ffmpeg -v error -y -i "$TMP/$mode-film.mp4" -vf "fps=${TOTAL}/${dur}" -frames:v $TOTAL -q:v 4 "frames/$mode/%04d.jpg"
  echo "$mode: $(ls frames/$mode | wc -l) frames, $(du -sh frames/$mode | cut -f1)"
}
build desktop 1600 900
build mobile 720 1280
