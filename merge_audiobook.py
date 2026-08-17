#!/usr/bin/env python3
"""
Merge all generated MP3 parts into one complete audiobook.
Usage: python3 merge_audiobook.py
"""
import os
import json

def merge_mp3s(input_dir, output_file):
    """Concatenate MP3 files in order."""
    # Get list of mp3 files sorted by part number
    mp3_files = sorted([f for f in os.listdir(input_dir) if f.startswith('part_') and f.endswith('.mp3')],
                       key=lambda x: int(x.split('_')[1].split('.')[0]))
    
    if not mp3_files:
        print("No MP3 files found!")
        return
    
    print(f"Found {len(mp3_files)} MP3 files to merge")
    
    # For MP3 files with the same encoding, simple binary concatenation works
    # This is a valid approach for MP3s from the same source
    with open(output_file, 'wb') as outfile:
        for i, mp3_file in enumerate(mp3_files):
            filepath = os.path.join(input_dir, mp3_file)
            size = os.path.getsize(filepath)
            print(f"  Appending {mp3_file} ({size/1024:.1f} KB)...")
            with open(filepath, 'rb') as infile:
                outfile.write(infile.read())
    
    final_size = os.path.getsize(output_file)
    print(f"\nMerged audiobook saved to: {output_file}")
    print(f"Total size: {final_size/1024/1024:.1f} MB")
    print(f"Total clips: {len(mp3_files)}")
    
    # Also check chunk_info.json for part mapping
    info_path = os.path.join(input_dir, 'chunk_info.json')
    if os.path.exists(info_path):
        with open(info_path) as f:
            info = json.load(f)
        print(f"\nChunks defined: {len(info)}")
    
    return output_file

if __name__ == '__main__':
    input_dir = '/home/user/Burn-videos-here/segments'
    output_file = '/home/user/Burn-videos-here/100M_Money_Models_Audiobook.mp3'
    merge_mp3s(input_dir, output_file)