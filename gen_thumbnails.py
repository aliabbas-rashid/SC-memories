#!/usr/bin/env python3
import subprocess
from pathlib import Path

MEDIA_DIR = Path("media")
THUMB_DIR = Path("thumbnails")
VIDEO_EXTENSIONS = [".mp4", ".mov", ".avi", ".mkv"]

THUMB_DIR.mkdir(exist_ok=True)

def generate_thumbnail(video_path: Path, thumb_path: Path):
    """
    Generates a thumbnail (JPEG) for a video using ffmpeg.
    Captures the frame at 1 second into the video.
    """
    try:
        cmd = [
            "ffmpeg",
            "-y",             # overwrite if exists
            "-i", str(video_path),
            "-ss", "00:00:01",  # seek to 1 second
            "-vframes", "1",    # capture 1 frame
            str(thumb_path)
        ]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"Generated thumbnail: {thumb_path.name}")
    except Exception as e:
        print(f"Failed to generate thumbnail for {video_path.name}: {e}")

def main():
    for video_file in MEDIA_DIR.iterdir():
        if video_file.suffix.lower() in VIDEO_EXTENSIONS:
            thumb_file = THUMB_DIR / f"{video_file.stem}.jpg"
            if not thumb_file.exists():
                generate_thumbnail(video_file, thumb_file)
            else:
                print(f"Thumbnail already exists: {thumb_file.name}")

if __name__ == "__main__":
    main()
