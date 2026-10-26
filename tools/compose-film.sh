#!/usr/bin/env bash
# Joins real footage into one 535-frame film, for desktop and phone. Every chapter is a real person, no renders.
#   0 street at night  ->  1 buttoning a white shirt  ->  2 buttoning the waistcoat  ->  3 the tailor chalks the cloth,
#   then fits the jacket on a client  ->  4 buttoning the jacket  ->  5 three men on the steps  ->  6 cufflinks close-up
# Footage is from Pexels (Pexels License), see footage/CREDITS.txt.
set -euo pipefail
cd "$(dirname "$0")/.."
FPS=24; X=0.4; TOTAL=535
TMP=build/compose; rm -rf "$TMP"; mkdir -p "$TMP"
# one dark green noir grade across every clip
GRADE="eq=contrast=1.15:brightness=-0.09:saturation=0.5,colorbalance=rs=-0.04:gs=0.015:bs=-0.03:rm=-0.03:gm=0.01:bm=-0.01,vignette=angle=PI/4"

build() { # mode W H
  local mode=$1 W=$2 H=$3 cover="scale=$2:$3:force_original_aspect_ratio=increase,crop=$2:$3"
  # pos P: a 9:16 window slid P of the way across the frame (phones), or the cover crop (desktop)
  pos() { if [ "$mode" = mobile ]; then echo "crop=ih*9/16:ih:(iw-ih*9/16)*$1:0,scale=$W:$H:flags=lanczos"; else echo "$cover"; fi; }
  local cuff fitting
  if [ "$mode" = mobile ]; then cuff="$cover"; fitting=$(pos 0.43)
  else cuff="crop=1080:608:0:420,scale=$W:$H:flags=lanczos"; fitting="crop=iw*0.7:ih*0.7:0:ih*0.15,scale=$W:$H:flags=lanczos"; fi
  clip() { ffmpeg -v error -y -ss "$2" -t "$3" -i "footage/$1.mp4" -an -vf "$4,fps=$FPS,$GRADE,format=yuv420p" -c:v libx264 -crf 12 -preset veryfast "$TMP/$mode-$5.mp4"; }
  clip walk-night 4.0 2.7 "$cover" a
  clip shirt 0.5 3.46 "$(pos 0.38)" s
  clip waistcoat 1.0 3.37 "$(pos 0.43)" w
  clip chalk 3.0 3.16 "$(pos 0.21)" k
  clip fitting 5.0 3.585 "$fitting" f
  clip buttoning 1.0 2.6 "$cover" c
  clip three-men 2.5 3.31 "$cover" d
  clip cufflinks 0.5 2.95 "$cuff" e
  # dissolves land between the chapter windows in index.html (frames 60, 133, 204, 270, 337, 401, 470)
  ffmpeg -v error -y -i "$TMP/$mode-a.mp4" -i "$TMP/$mode-s.mp4" -i "$TMP/$mode-w.mp4" -i "$TMP/$mode-k.mp4" -i "$TMP/$mode-f.mp4" \
    -i "$TMP/$mode-c.mp4" -i "$TMP/$mode-d.mp4" -i "$TMP/$mode-e.mp4" -filter_complex \
    "[0][1]xfade=transition=fade:duration=$X:offset=2.3[v1];[v1][2]xfade=transition=fade:duration=$X:offset=5.36[v2];[v2][3]xfade=transition=fade:duration=$X:offset=8.33[v3];[v3][4]xfade=transition=fade:duration=$X:offset=11.09[v4];[v4][5]xfade=transition=fade:duration=$X:offset=14.275[v5];[v5][6]xfade=transition=fadeblack:duration=$X:offset=16.47[v6];[v6][7]xfade=transition=fade:duration=$X:offset=19.38,fade=t=out:st=21.7:d=0.6[v]" \
    -map "[v]" -c:v libx264 -crf 14 -preset veryfast "$TMP/$mode-film.mp4"
  local dur; dur=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$TMP/$mode-film.mp4")
  rm -rf "frames/$mode"; mkdir -p "frames/$mode"
  ffmpeg -v error -y -i "$TMP/$mode-film.mp4" -vf "fps=${TOTAL}/${dur}" -frames:v $TOTAL -q:v 4 "frames/$mode/%04d.jpg"
  echo "$mode: $(ls frames/$mode | wc -l) frames, $(du -sh frames/$mode | cut -f1)"
}
build desktop 1600 900
build mobile 720 1280
