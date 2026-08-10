#!/usr/bin/env bash
set -euo pipefail
ROOT="Relationships psychology/Week 1"
FFMPEG="$(python - <<'PY'
import imageio_ffmpeg
print(imageio_ffmpeg.get_ffmpeg_exe())
PY
)"
rm -rf /tmp/day2_clips /tmp/day2_concat.txt
mkdir -p /tmp/day2_clips
python - <<'PY'
import json
x=json.load(open('Relationships psychology/Week 1/day2_fresh_segmentation.json'))
for i,a in enumerate(x,1):
    dur=a['end']-a['start']; frames=round(dur*30)
    direction='in' if i%2 else 'out'
    z="min(zoom+0.00018,1.08)" if direction=='in' else "max(zoom-0.00018,1.0)"
    open('/tmp/day2_clip_args','a').write(f"{i}|{dur:.3f}|{frames}|{z}\n")
PY
while IFS='|' read -r i dur frames z; do
  "$FFMPEG" -loglevel error -loop 1 -t "$dur" -i "$ROOT/day2_fresh_$(printf '%03d' "$i").png" -vf "scale=1280:720:force_original_aspect_ratio=increase,crop=1280:720,zoompan=z='$z':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=$frames:s=1280x720:fps=30,setsar=1,format=yuv420p" -an -c:v libx264 -preset ultrafast -crf 23 -y "/tmp/day2_clips/$(printf '%03d' "$i").mp4"
  printf "file '/tmp/day2_clips/%03d.mp4'\n" "$i" >> /tmp/day2_concat.txt
done < /tmp/day2_clip_args
"$FFMPEG" -loglevel error -f concat -safe 0 -i /tmp/day2_concat.txt -i "$ROOT/Have you ever tried .mp3" -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart -y "$ROOT/Day 2 - Validation is not agreement.mp4"
ls -lh "$ROOT/Day 2 - Validation is not agreement.mp4"
