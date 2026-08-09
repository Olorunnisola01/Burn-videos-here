#!/usr/bin/env python3
"""
Video Assembly Pipeline v4 - Smooth Motion
- Gentle Ken Burns zoom (all same direction, subtle range)
- Smooth pan motion for organic feel
- Clean cuts without jitter
- 1920x1080 @ 30fps
"""

import subprocess
import os

FFMPEG = subprocess.check_output(['python3', '-c', 
    'import imageio_ffmpeg; print(imageio_ffmpeg.get_ffmpeg_exe())']).decode().strip()

BASE_DIR = "/home/user/Burn-videos-here"
IMG_DIR = os.path.join(BASE_DIR, "images")
AUDIO_FILE = os.path.join(BASE_DIR, "The Decision That Ch.mp3")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
CLIPS_DIR = os.path.join(OUTPUT_DIR, "clips_v4_smooth")

os.makedirs(CLIPS_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

SEGMENTS = [
    ("img_001.png", 0, 4),
    ("img_002.png", 4, 3),
    ("img_003.png", 7, 2),
    ("img_004.png", 9, 5),
    ("img_005.png", 14, 6),
    ("img_006.png", 20, 9),
    ("img_007.png", 29, 8),
    ("img_008.png", 37, 7),
    ("img_009.png", 44, 7),
    ("img_010.png", 51, 3),
    ("img_011.png", 54, 9),
    ("img_012.png", 63, 6),
    ("img_013.png", 69, 8),
    ("img_014.png", 77, 6),
    ("img_015.png", 83, 9),
    ("img_016.png", 92, 5),
    ("img_017.png", 97, 7),
    ("img_018.png", 104, 6),
    ("img_019.png", 110, 3),
    ("img_020.png", 113, 12),
    ("img_021.png", 125, 4),
    ("img_022.png", 129, 11),
    ("img_023.png", 140, 9),
    ("img_024.png", 149, 9),
    ("img_025.png", 158, 10),
    ("img_026.png", 168, 14),
    ("img_027.png", 182, 5),
    ("img_028.png", 187, 8),
    ("img_029.png", 195, 7),
    ("img_030.png", 202, 11),
    ("img_031.png", 213, 11),
    ("img_032.png", 224, 8),
    ("img_033.png", 232, 6),
    ("img_034.png", 238, 9),
    ("img_035.png", 247, 7),
    ("img_036.png", 254, 3.49),
]

FPS = 30
WIDTH = 1920
HEIGHT = 1080


def create_clip(img_path, output_path, duration, motion_type="zoom_in_pan_right"):
    """Create a clip with smooth Ken Burns motion - all zoom-in, subtle range"""
    total_frames = max(int(duration * FPS), 1)
    
    if motion_type == "zoom_in_pan_right":
        zoom_expr = "min(zoom+0.000267,1.08)"
        x_expr = "iw/2-(iw/zoom/2)+on*0.3"
        y_expr = "ih/2-(ih/zoom/2)"
    elif motion_type == "zoom_in_pan_left":
        zoom_expr = "min(zoom+0.000267,1.08)"
        x_expr = "iw/2-(iw/zoom/2)-on*0.3"
        y_expr = "ih/2-(ih/zoom/2)"
    else:
        zoom_expr = "min(zoom+0.000267,1.08)"
        x_expr = "iw/2-(iw/zoom/2)"
        y_expr = "ih/2-(ih/zoom/2)"
    
    vf = (
        f"scale=8000:-1,"
        f"zoompan=z='{zoom_expr}':x='{x_expr}':y='{y_expr}'"
        f":d={total_frames}:s={WIDTH}x{HEIGHT}:fps={FPS},"
        f"format=yuv420p"
    )
    
    cmd = [
        FFMPEG, '-y',
        '-loop', '1', '-i', img_path,
        '-vf', vf,
        '-t', str(duration),
        '-c:v', 'libx264',
        '-preset', 'fast',
        '-crf', '18',
        '-pix_fmt', 'yuv420p',
        output_path
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if result.returncode != 0:
        print(f"  ERROR: {result.stderr[-300:]}")
        return False
    return True


def main():
    print("🎬 VIDEO ASSEMBLY PIPELINE v4 - Smooth Motion")
    print(f"   FFmpeg: {FFMPEG}")
    print(f"   Images: {len(SEGMENTS)} segments")
    print(f"   Motion: Subtle zoom-in (1.0→1.08) with gentle pan")
    print()
    
    n = len(SEGMENTS)
    motion_types = ["zoom_in_pan_right", "zoom_in_pan_left", "zoom_in_center"]
    
    print("=" * 60)
    print("STEP 1: Generating clips with smooth Ken Burns motion")
    print("=" * 60)
    
    for i, (img_name, start, duration) in enumerate(SEGMENTS):
        clip_path = os.path.join(CLIPS_DIR, f"clip_{i+1:03d}.mp4")
        
        if os.path.exists(clip_path) and os.path.getsize(clip_path) > 10000:
            print(f"  [{i+1:02d}/{n}] {img_name} - SKIP (exists)")
            continue
        
        img_path = os.path.join(IMG_DIR, img_name)
        motion_type = motion_types[i % 3]
        
        print(f"  [{i+1:02d}/{n}] {img_name} ({duration:.1f}s, {motion_type})...", end=" ", flush=True)
        success = create_clip(img_path, clip_path, duration, motion_type)
        print("✓" if success else "✗ FAILED")
    
    print("\n" + "=" * 60)
    print("STEP 2: Concatenating clips (clean cuts)")
    print("=" * 60)
    
    concat_list = os.path.join(OUTPUT_DIR, "concat_list_v4.txt")
    with open(concat_list, 'w') as f:
        for i in range(n):
            clip_path = os.path.join(CLIPS_DIR, f"clip_{i+1:03d}.mp4")
            f.write(f"file '{clip_path}'\n")
    
    video_no_audio = os.path.join(OUTPUT_DIR, "video_v4_no_audio.mp4")
    
    cmd = [
        FFMPEG, '-y',
        '-f', 'concat', '-safe', '0', '-i', concat_list,
        '-c:v', 'libx264', '-preset', 'medium', '-crf', '18',
        '-pix_fmt', 'yuv420p',
        video_no_audio
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    if result.returncode != 0:
        print(f"  ERROR: {result.stderr[-500:]}")
        return
    print("  ✓ Video concatenated")
    
    print("\n" + "=" * 60)
    print("STEP 3: Adding narration audio")
    print("=" * 60)
    
    output_path = os.path.join(OUTPUT_DIR, "The_Decision_That_Changes_Everything.mp4")
    
    cmd = [
        FFMPEG, '-y',
        '-i', video_no_audio,
        '-i', AUDIO_FILE,
        '-c:v', 'copy',
        '-c:a', 'aac',
        '-b:a', '192k',
        '-shortest',
        '-map', '0:v:0',
        '-map', '1:a:0',
        output_path
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if result.returncode != 0:
        print(f"  ERROR: {result.stderr[-500:]}")
        return
    
    size = os.path.getsize(output_path)
    print(f"  ✓ Final video: {output_path}")
    print(f"  File size: {size / (1024*1024):.1f} MB")
    
    print("\n" + "=" * 60)
    print("STEP 4: Verification")
    print("=" * 60)
    
    result = subprocess.run([FFMPEG, '-i', output_path], capture_output=True, text=True)
    for line in result.stderr.split('\n'):
        if 'Duration' in line or 'Stream' in line:
            print(f"  {line.strip()}")
    
    print("\n" + "=" * 60)
    print("✅ PIPELINE COMPLETE - Smooth motion!")
    print("=" * 60)


if __name__ == "__main__":
    main()
