"""
Transcription Engine - Singleton Pattern
Manages Faster-Whisper model with GPU auto-detection.
"""

import os
from typing import ClassVar, Optional
import torch
from faster_whisper import WhisperModel


class TranscriptionEngine:
    """
    Singleton transcription engine using Faster-Whisper.
    Loads the model once and reuses it for all transcriptions.
    """

    _instance: ClassVar[Optional["TranscriptionEngine"]] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self.device, self.compute_type = self._detect_hardware()
        self.model_size = os.getenv("WHISPER_MODEL", "tiny")

        print(f"Loading Whisper model '{self.model_size}' on {self.device} ({self.compute_type})...")
        self.model = WhisperModel(
            self.model_size,
            device=self.device,
            compute_type=self.compute_type,
            download_root="./models"
        )
        self._initialized = True
        print(f"✓ Model loaded successfully")

    @staticmethod
    def _detect_hardware() -> tuple[str, str]:
        """
        Detect available hardware and return optimal device and compute type.

        Returns:
            tuple: (device, compute_type)
                - device: "cuda" or "cpu"
                - compute_type: "float16" (GPU) or "int8" (CPU)
        """
        if torch.cuda.is_available():
            device = "cuda"
            compute_type = "float16"
            print(f"✓ GPU detected: {torch.cuda.get_device_name(0)}")
        else:
            device = "cpu"
            compute_type = "int8"
            print("ℹ No GPU detected. Using CPU with int8 quantization.")

        return device, compute_type

    def transcribe(self, audio_path: str, language: Optional[str] = None) -> dict:
        """
        Transcribe audio file.

        Args:
            audio_path: Path to audio/video file
            language: Optional language code (e.g., 'es', 'en')

        Returns:
            dict: {
                "language": str,
                "language_probability": float,
                "segments": [{"start": float, "end": float, "text": str}],
                "text": str (full transcription)
            }
        """
        print(f"Transcribing: {audio_path}")

        segments, info = self.model.transcribe(
            audio_path,
            language=language,
            beam_size=5
        )

        # Collect segments
        segments_list = []
        full_text = []

        for segment in segments:
            seg_dict = {
                "start": round(segment.start, 2),
                "end": round(segment.end, 2),
                "text": segment.text.strip()
            }
            segments_list.append(seg_dict)
            full_text.append(seg_dict["text"])

        return {
            "language": info.language,
            "language_probability": float(info.language_probability),
            "segments": segments_list,
            "text": " ".join(full_text)
        }

    @classmethod
    def get_instance(cls) -> "TranscriptionEngine":
        """Get or create the singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @property
    def ready(self) -> bool:
        """Check if the engine is ready to transcribe."""
        return self._initialized and self.model is not None

    @property
    def gpu_available(self) -> bool:
        """Check if GPU is available."""
        return self.device == "cuda"
