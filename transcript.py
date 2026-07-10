#!/usr/bin/env python3
"""
Meeting Transcription Tool
Usage: python transcribe_meeting.py <folder_with_videos>
Output: A single .md file with full transcript, sorted oldest-to-newest
"""

import os
import sys
import subprocess
import argparse
from datetime import datetime
from pathlib import Path

# ── CONFIG ────────────────────────────────────────────────────────────────────
WHISPER_MODEL = "large"          # Options: tiny, base, small, medium, large
VIDEO_EXTENSIONS = {".mp4", ".mkv", ".mov", ".avi", ".webm", ".m4v"}
AUDIO_EXTENSIONS = {".mp3", ".wav", ".m4a", ".ogg", ".flac"}
# ──────────────────────────────────────────────────────────────────────────────


def check_dependencies():
    """Make sure ffmpeg and whisper are available."""
    errors = []
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
    except (FileNotFoundError, subprocess.CalledProcessError):
        errors.append("ffmpeg not found. Install from https://ffmpeg.org/download.html")

    try:
        import whisper  # noqa: F401
    except ImportError:
        errors.append("openai-whisper not found. Run: pip install openai-whisper")

    if errors:
        print("Missing dependencies:")
        for e in errors:
            print(f"  ✗ {e}")
        sys.exit(1)


def find_media_files(folder: Path) -> list[Path]:
    """Find all video/audio files and sort by modification time (oldest first)."""
    all_extensions = VIDEO_EXTENSIONS | AUDIO_EXTENSIONS
    files = [
        f for f in folder.iterdir()
        if f.is_file() and f.suffix.lower() in all_extensions
    ]
    if not files:
        print(f"No media files found in {folder}")
        sys.exit(1)
    files.sort(key=lambda f: f.stat().st_mtime)
    return files


def extract_audio(video_path: Path, output_dir: Path) -> Path:
    """Extract audio from video to a temp WAV file. Skip if already audio."""
    if video_path.suffix.lower() in AUDIO_EXTENSIONS:
        return video_path  # Already audio, use directly

    audio_path = output_dir / (video_path.stem + "_audio.wav")
    if audio_path.exists():
        print(f"  (using cached audio for {video_path.name})")
        return audio_path

    print(f"  Extracting audio from {video_path.name}...")
    subprocess.run([
        "ffmpeg", "-i", str(video_path),
        "-vn",                    # no video
        "-acodec", "pcm_s16le",   # WAV format
        "-ar", "16000",           # 16kHz (whisper optimal)
        "-ac", "1",               # mono
        "-y",                     # overwrite
        str(audio_path)
    ], capture_output=True, check=True)
    return audio_path


def transcribe_audio(audio_path: Path, model) -> dict:
    """Transcribe audio file using Whisper. Returns result dict."""
    print(f"  Transcribing {audio_path.name}...")
    result = model.transcribe(
        str(audio_path),
        verbose=False,
        task="transcribe",
        word_timestamps=False,
    )
    return result


def format_timestamp(seconds: float) -> str:
    """Convert seconds to HH:MM:SS format."""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


def build_transcript_block(filename: str, result: dict, file_index: int, total: int) -> str:
    """Format one file's transcript as a markdown section."""
    lines = [
        f"## File {file_index}/{total}: {filename}",
        "",
    ]

    # Add segments with timestamps
    for segment in result.get("segments", []):
        ts = format_timestamp(segment["start"])
        text = segment["text"].strip()
        if text:
            lines.append(f"[{ts}] {text}")

    lines.append("")  # blank line between sections
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Transcribe a folder of meeting videos into a single markdown file."
    )
    parser.add_argument(
        "folder",
        nargs="?",
        default=str(Path(__file__).parent),
        help="Folder containing video/audio files (default: script's own folder)"
    )
    parser.add_argument(
        "--model",
        default=WHISPER_MODEL,
        choices=["tiny", "base", "small", "medium", "large"],
        help=f"Whisper model to use (default: {WHISPER_MODEL})"
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Output .md file path (default: <folder>/transcript_YYYY-MM-DD.md)"
    )
    args = parser.parse_args()

    folder = Path(args.folder).resolve()
    if not folder.is_dir():
        print(f"Error: '{folder}' is not a valid directory.")
        sys.exit(1)

    print("Checking dependencies...")
    check_dependencies()

    import whisper

    # Find files
    media_files = find_media_files(folder)
    print(f"\nFound {len(media_files)} media file(s) (oldest → newest):")
    for f in media_files:
        mtime = datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
        print(f"  {mtime}  {f.name}")

    # Load model
    print(f"\nLoading Whisper model '{args.model}' (downloads once, cached after)...")
    model = whisper.load_model(args.model)
    print("Model loaded.\n")

    # Temp dir for extracted audio
    temp_dir = folder / "_temp_audio"
    temp_dir.mkdir(exist_ok=True)

    # Transcribe each file
    transcript_blocks = []
    total = len(media_files)

    for i, media_file in enumerate(media_files, start=1):
        print(f"[{i}/{total}] Processing: {media_file.name}")
        try:
            audio_path = extract_audio(media_file, temp_dir)
            result = transcribe_audio(audio_path, model)
            block = build_transcript_block(media_file.name, result, i, total)
            transcript_blocks.append(block)
            print(f"  ✓ Done\n")
        except Exception as e:
            print(f"  ✗ Failed: {e}\n")
            transcript_blocks.append(f"## File {i}/{total}: {media_file.name}\n\n[TRANSCRIPTION FAILED: {e}]\n")

    # Build output file
    date_str = datetime.now().strftime("%Y-%m-%d")
    output_path = Path(args.output) if args.output else folder / f"transcript_{date_str}.md"

    header = f"""# Meeting Transcript
Date: {date_str}
Files: {total}
Model: {args.model}

---

"""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(header)
        f.write("\n".join(transcript_blocks))

    print(f"✓ Transcript saved to: {output_path}")

    # Clean up temp audio files
    for temp_file in temp_dir.glob("*.wav"):
        temp_file.unlink()
    try:
        temp_dir.rmdir()
    except OSError:
        pass


if __name__ == "__main__":
    main()
    input("\nPress Enter to close...")