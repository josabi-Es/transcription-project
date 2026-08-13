import json
import os
import tempfile
from pathlib import Path

from fastapi import UploadFile


SUPPORTED_FORMATS = {
    ".mp3", ".wav", ".m4a", ".flac", ".ogg", ".aac", ".wma",
    ".mp4", ".avi", ".mov", ".mkv", ".webm", ".flv", ".wmv", ".3gp",
}


def _seconds_to_hms(seconds: float) -> str:
    total = int(seconds)
    h = total // 3600
    m = (total % 3600) // 60
    s = total % 60
    return f"{h:02d}:{m:02d}:{s:02d}"


def _get_output_dir() -> Path:
    output_dir = Path(os.getenv("OUTPUT_DIR", "./storage/output"))
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def get_output_path(original_filename: str, extension: str = ".json") -> Path:
    stem = Path(original_filename).stem
    return _get_output_dir() / f"{stem}{extension}"


def save_transcription(result: dict, original_filename: str) -> Path:
    output_path = get_output_path(original_filename)

    payload = {
        "metadata": {
            "date": result["date"],
            "file": result["file"],
            "language": result["language"],
            "language_probability": result["language_probability"],
            "video_duration_seconds": result["video_duration_seconds"],
            "processing_time_seconds": result["processing_time_seconds"],
            "speed_factor": result["speed_factor"],
            "model": result["model"],
        },
        "full_text": result["text"],
        "clean_segments": [
            {"time": _seconds_to_hms(seg["start"]), "text": seg["text"]}
            for seg in result["segments"]
        ],
    }

    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return output_path


def is_supported_media(filename: str) -> bool:
    return Path(filename).suffix.lower() in SUPPORTED_FORMATS


async def save_upload_to_temp(file: UploadFile) -> str:
    if not is_supported_media(file.filename):
        raise ValueError(
            f"Unsupported file format: {file.filename}. "
            f"Supported: {', '.join(sorted(SUPPORTED_FORMATS))}"
        )

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
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        print(f"Warning: Could not delete temporary file {file_path}: {e}")
