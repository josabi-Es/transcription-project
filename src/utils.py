"""
Utility functions for the transcription project.
"""

from pathlib import Path


SUPPORTED_FORMATS = {".mp4", ".avi", ".mov", ".mkv", ".webm", ".flv", ".wmv"}


def is_valid_video_file(file_path: str) -> bool:
    """
    Check if a file is a valid video format.

    Args:
        file_path: Path to the file

    Returns:
        bool: True if valid video format, False otherwise
    """
    path = Path(file_path)
    return path.suffix.lower() in SUPPORTED_FORMATS


def get_output_filename(video_path: str, extension: str = ".txt") -> str:
    """
    Generate output filename based on video filename.

    Args:
        video_path: Path to the video file
        extension: Output file extension (default: .txt)

    Returns:
        str: Output filename in same directory as video
    """
    path = Path(video_path)
    return str(path.parent / f"{path.stem}_transcript{extension}")
