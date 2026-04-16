"""
Utility functions for file handling and validation.
"""

import os
import tempfile
from pathlib import Path
from fastapi import UploadFile


SUPPORTED_FORMATS = {".mp3", ".wav", ".m4a", ".flac", ".ogg", ".aac", ".wma", ".mp4", ".avi", ".mov", ".mkv", ".webm", ".flv", ".wmv", ".3gp"}


def is_supported_media(filename: str) -> bool:
    """
    Check if file has a supported audio/video format.

    Args:
        filename: File name to check

    Returns:
        bool: True if supported format, False otherwise
    """
    suffix = Path(filename).suffix.lower()
    return suffix in SUPPORTED_FORMATS


async def save_upload_to_temp(file: UploadFile) -> str:
    """
    Save an uploaded file to a temporary location.

    Args:
        file: FastAPI UploadFile object

    Returns:
        str: Path to the temporary file

    Raises:
        ValueError: If file format is not supported
    """
    if not is_supported_media(file.filename):
        raise ValueError(f"Unsupported file format: {file.filename}. Supported: {', '.join(sorted(SUPPORTED_FORMATS))}")

    # Create temp file with original extension
    suffix = Path(file.filename).suffix
    temp_file = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)

    try:
        contents = await file.read()
        temp_file.write(contents)
        temp_file.close()
        return temp_file.name
    except Exception as e:
        temp_file.close()
        if os.path.exists(temp_file.name):
            os.remove(temp_file.name)
        raise ValueError(f"Error saving upload: {str(e)}")


def cleanup_temp(file_path: str) -> None:
    """
    Remove a temporary file.

    Args:
        file_path: Path to the temporary file
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        print(f"Warning: Could not delete temporary file {file_path}: {e}")
