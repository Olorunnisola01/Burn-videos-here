#!/usr/bin/env bash
set -euo pipefail
ROOT="Relationships psychology/Week 1"
FFMPEG="$(python - <<'PY'
import imageio_ffmpeg
print(imageio_ffmpeg.get_ffmpeg_exe())
PY
)"
OUT="$ROOT/Day 2 - Validation is not agreement.mp4"
# Generate a single FFmpeg filter graph from the authoritative timing segmentation.
python - <<'PY' > /tmp/day2_ffmpeg_args.txt
import json
x=json.load(open('Relationships psychology/Week 1/day2_fresh_segmentation.json'))
trans=['fade','slideright','slideleft','fadeblack','fadewhite']
args=[]
for i,a in enumerate(x,1):
    dur=a['end']-a['start']; args += ['-loop','1','-t',f'{dur:.3f}','-i',f'Relationships psychology/Week 1/day2_fresh_{i:03d}.png']
parts=[]
for i,a in enumerate(x):
    dur=a['end']-a['start']; frames=round(dur*30)
    direction='in' if i%2==0 else 'out'
    if direction=='in': z=f"min(zoom+0.00018,1.08)"
    else: z=f"max(zoom-0.00018,1.0)"
    parts.append(f"[{i}:v]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,zoompan=z='{z}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s=1920x1080:fps=30,setsar=1,settb=1/30[v{i+1}]")
labels=''.join(f'[v{i}]' for i in range(1,len(x)+1))
parts.append(f"{labels}concat=n={len(x)}:v=1:a=0[vfinal]")
filtergraph=';'.join(parts)
args += ['-i', 'Relationships psychology/Week 1/Have you ever tried .mp3']
args += ['-filter_complex',filtergraph,'-map','[vfinal]','-map',f'{len(x)}:a','-c:v','libx264','-preset','veryfast','-crf','20','-pix_fmt','yuv420p','-r','30','-c:a','aac','-b:a','192k','-shortest','-movflags','+faststart','-y', 'Relationships psychology/Week 1/Day 2 - Validation is not agreement.mp4']
print(' '.join("'"+a.replace("'","'\\''")+"'" for a in args))
PY
# shellcheck disable=SC2046
eval "\"$FFMPEG\" $(cat /tmp/day2_ffmpeg_args.txt)"
rm -f /tmp/day2_ffmpeg_args.txt
ls -lh "$OUT"
