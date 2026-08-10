import json, subprocess
from pathlib import Path
import imageio_ffmpeg
root=Path('Relationships psychology/Week 1'); seg=json.loads((root/'day2_fresh_segmentation.json').read_text())
listp=Path('/tmp/day2_images.txt')
with listp.open('w') as f:
 for i,a in enumerate(seg,1):
  f.write(f"file '{(root/f'day2_fresh_{i:03d}.png').resolve()}'\n")
  f.write(f"duration {a['end']-a['start']:.3f}\n")
 f.write(f"file '{(root/f'day2_fresh_{len(seg):03d}.png').resolve()}'\n")
out=root/'Day 2 - Validation is not agreement.mp4'; ff=imageio_ffmpeg.get_ffmpeg_exe()
subprocess.run([ff,'-loglevel','error','-f','concat','-safe','0','-i',str(listp),'-i',str(root/'Have you ever tried .mp3'),'-vf','scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2,format=yuv420p','-map','0:v','-map','1:a','-c:v','libx264','-preset','ultrafast','-crf','23','-r','30','-c:a','aac','-b:a','192k','-shortest','-movflags','+faststart','-y',str(out)],check=True)
print(out, out.stat().st_size)
