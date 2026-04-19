"""
Transcription Engine - Singleton Pattern
Manages Faster-Whisper model with GPU auto-detection.
"""

import os
import sys
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

        self._load_cuda_path()
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
    def _load_cuda_path() -> None:
        """Add CUDA_BIN_PATH from .env to DLL search path (Windows only)."""
        cuda_bin = os.getenv("CUDA_BIN_PATH", "").strip()
        if cuda_bin and sys.platform == "win32":
            if os.path.isdir(cuda_bin):
                os.add_dll_directory(cuda_bin)
                print(f"✓ CUDA DLL path added: {cuda_bin}")
            else:
                print(f"⚠ CUDA_BIN_PATH not found: {cuda_bin}")

    @staticmethod
    def _detect_hardware() -> tuple[str, str]:
        """
        Detect available hardware and return optimal device and compute type.
        Controlled via WHISPER_DEVICE env var: gpu | cpu | auto (default: gpu)

        Returns:
            tuple: (device, compute_type)
                - device: "cuda" or "cpu"
                - compute_type: "float16" (GPU) or "int8" (CPU)
        """
        setting = os.getenv("WHISPER_DEVICE", "gpu").lower()

        if setting == "cpu":
            print("ℹ WHISPER_DEVICE=cpu. Forcing CPU mode.")
            return "cpu", "int8"

        if setting in ("gpu", "auto"):
            if torch.cuda.is_available():
                print(f"✓ GPU detected: {torch.cuda.get_device_name(0)}")
                return "cuda", "float16"
            else:
                print("ℹ No GPU found. Falling back to CPU.")
                return "cpu", "int8"

        print(f"⚠ Unknown WHISPER_DEVICE='{setting}', falling back to CPU.")
        return "cpu", "int8"

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

        beam_size = int(os.getenv("WHISPER_BEAM_SIZE", "5"))
        vad_filter = os.getenv("WHISPER_VAD_FILTER", "false").lower() == "true"
        condition_on_previous_text = os.getenv("WHISPER_CONDITION_ON_PREVIOUS_TEXT", "true").lower() == "true"

        segments, info = self.model.transcribe(
            audio_path,
            language=language,
            beam_size=beam_size,
            vad_filter=vad_filter,
            condition_on_previous_text=condition_on_previous_text,
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
