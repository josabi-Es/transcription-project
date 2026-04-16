#!/usr/bin/env python3
"""
Transcription Project - Main Entry Point
Transcribe video files using Faster-Whisper with automatic GPU detection.
"""

import sys
import argparse
from pathlib import Path
from transcriber import transcribe_video


def main():
    parser = argparse.ArgumentParser(
        description="Transcribe video files using Faster-Whisper",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py video.mp4
  python main.py video.mp4 --model large-v3
  python main.py video.mp4 --model base --language es
        """
    )

    parser.add_argument("video", help="Path to video file (mp4, avi, mov, mkv, etc.)")
    parser.add_argument(
        "--model",
        default="tiny",
        choices=["tiny", "base", "small", "medium", "large-v3"],
        help="Model size (default: tiny)"
    )
    parser.add_argument(
        "--language",
        default=None,
        help="Language code (e.g., 'es', 'en'). Auto-detect if not specified."
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Output file for transcription (optional). If not specified, prints to console."
    )

    args = parser.parse_args()

    # Validate video file exists
    video_path = Path(args.video)
    if not video_path.exists():
        print(f"Error: Video file not found: {args.video}", file=sys.stderr)
        sys.exit(1)

    # Transcribe
    print(f"Starting transcription: {args.video}")
    print(f"Model: {args.model}")
    print("-" * 60)

    transcription = transcribe_video(
        str(video_path),
        model_size=args.model,
        language=args.language
    )

    # Output
    if args.output:
        output_path = Path(args.output)
        output_path.write_text(transcription, encoding="utf-8")
        print("-" * 60)
        print(f"Transcription saved to: {args.output}")
    else:
        print("-" * 60)
        print("TRANSCRIPTION:\n")
        print(transcription)


if __name__ == "__main__":
    main()
