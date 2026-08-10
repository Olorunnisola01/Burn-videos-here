import json, subprocess, os
from pathlib import Path
import imageio_ffmpeg
root=Path('Relationships psychology/Week 1'); clipdir=Path('/tmp/day2_clips'); clipdir.mkdir(exist_ok=True)
ff=imageio_ffmpeg.get_ffmpeg_exe(); seg=json.loads((root/'day2_fresh_segmentation.json').read_text())
for i,a in enumerate(seg,1):
    out=clipdir/f'{i:03d}.mp4'
    dur=a['end']-a['start']; frames=round(dur*30)
    z="min(zoom+0.00018,1.08)" if i%2 else "max(zoom-0.00018,1.0)"
    vf=f"scale=1280:720:force_original_aspect_ratio=increase,crop=1280:720,zoompan=z='{z}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s=1280x720:fps=30,setsar=1,format=yuv420p"
    subprocess.run([ff,'-loglevel','error','-loop','1','-t',f'{dur:.3f}','-i',str(root/f'day2_fresh_{i:03d}.png'),'-vf',vf,'-an','-c:v','libx264','-preset','ultrafast','-crf','23','-y',str(out)],check=True)
with open('/tmp/day2_concat.txt','w') as f:
    for i in range(1,len(seg)+1): f.write(f"file '/tmp/day2_clips/{i:03d}.mp4'\n")
out=root/'Day 2 - Validation is not agreement.mp4'
subprocess.run([ff,'-loglevel','error','-f','concat','-safe','0','-i','/tmp/day2_concat.txt','-i',str(root/'Have you ever tried .mp3'),'-map','0:v','-map','1:a','-c:v','copy','-c:a','aac','-b:a','192k','-shortest','-movflags','+faststart','-y',str(out)],check=True)
print(out, out.stat().st_size)
