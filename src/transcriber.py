"""
Faster-Whisper Transcriber Module
Handles video transcription with automatic GPU detection.
"""

import torch
from faster_whisper import WhisperModel


def get_device_and_compute_type():
    """
    Detect available hardware and return optimal device and compute type.

    Returns:
        tuple: (device, compute_type)
            - device: "cuda" or "cpu"
            - compute_type: "float16" (GPU) or "int8" (CPU)
    """
    if torch.cuda.is_available():
        device = "cuda"
        compute_type = "float16"  # Optimized for NVIDIA GPUs
        print(f"✓ GPU detected: {torch.cuda.get_device_name(0)}")
    else:
        device = "cpu"
        compute_type = "int8"  # Optimized for CPU
        print("ℹ No GPU detected. Using CPU with int8 quantization.")

    return device, compute_type


def transcribe_video(
    video_path: str,
    model_size: str = "tiny",
    language: str = None
) -> str:
    """
    Transcribe a video file using Faster-Whisper.

    Args:
        video_path: Path to the video file
        model_size: Model size ("tiny", "base", "small", "medium", "large-v3")
        language: Optional language code (e.g., "es", "en")

    Returns:
        str: Full transcription text
    """
    device, compute_type = get_device_and_compute_type()

    # Load the Whisper model
    print(f"Loading model '{model_size}' ({compute_type})...")
    model = WhisperModel(
        model_size,
        device=device,
        compute_type=compute_type,
        download_root="./models"  # Store models locally
    )

    # Transcribe
    print(f"Transcribing: {video_path}")
    segments, info = model.transcribe(
        video_path,
        language=language,
        beam_size=5
    )

    # Collect results
    print(f"✓ Language detected: {info.language} (confidence: {info.language_probability:.2f})")
    print()

    transcription_text = []
    for segment in segments:
        line = f"[{format_timestamp(segment.start)} --> {format_timestamp(segment.end)}] {segment.text}"
        transcription_text.append(line)
        print(line)

    return "\n".join(transcription_text)


def format_timestamp(seconds: float) -> str:
    """Format seconds to HH:MM:SS"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"
