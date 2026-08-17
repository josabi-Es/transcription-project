import os
import sys
import time
from typing import ClassVar, Optional
import torch
from faster_whisper import WhisperModel


class TranscriptionEngine:
    """Singleton transcription engine using Faster-Whisper."""

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
        self.model_size = os.getenv("WHISPER_MODEL", "medium")

        print(f"Loading Whisper model '{self.model_size}' on {self.device} ({self.compute_type})...")
        models_dir = os.getenv("MODELS_DIR", "./storage/models")
        self.model = WhisperModel(
            self.model_size,
            device=self.device,
            compute_type=self.compute_type,
            download_root=models_dir,
        )
        self._initialized = True
        print("✓ Model loaded successfully")

    @staticmethod
    def _load_cuda_path() -> None:
        cuda_bin = os.getenv("CUDA_BIN_PATH", "").strip()
        if cuda_bin and sys.platform == "win32":
            if os.path.isdir(cuda_bin):
                os.add_dll_directory(cuda_bin)
                print(f"✓ CUDA DLL path added: {cuda_bin}")
            else:
                print(f"⚠ CUDA_BIN_PATH not found: {cuda_bin}")

    @staticmethod
    def _detect_hardware() -> tuple[str, str]:
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
        print(f"Transcribing: {audio_path}")

        beam_size = int(os.getenv("WHISPER_BEAM_SIZE", "3"))
        vad_filter = os.getenv("WHISPER_VAD_FILTER", "true").lower() == "true"
        condition_on_previous_text = os.getenv("WHISPER_CONDITION_ON_PREVIOUS_TEXT", "true").lower() == "true"
        initial_prompt = os.getenv("WHISPER_INITIAL_PROMPT", "").strip() or None

        t0 = time.time()
        segments, info = self.model.transcribe(
            audio_path,
            language=language,
            beam_size=beam_size,
            vad_filter=vad_filter,
            condition_on_previous_text=condition_on_previous_text,
            initial_prompt=initial_prompt,
        )
        processing_time = round(time.time() - t0, 2)

        segments_list = []
        full_text_parts = []

        for segment in segments:
            seg_dict = {
                "start": round(segment.start, 2),
                "end": round(segment.end, 2),
                "text": segment.text.strip(),
            }
            segments_list.append(seg_dict)
            full_text_parts.append(seg_dict["text"])

        video_duration = round(segments_list[-1]["end"], 2) if segments_list else 0.0
        speed_factor = round(video_duration / processing_time, 1) if processing_time > 0 else 0.0

        return {
            "language": info.language,
            "language_probability": float(info.language_probability),
            "segments": segments_list,
            "text": " ".join(full_text_parts),
            "video_duration_seconds": video_duration,
            "processing_time_seconds": processing_time,
            "speed_factor": speed_factor,
            "model": self.model_size,
        }

    @classmethod
    def get_instance(cls) -> "TranscriptionEngine":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @property
    def ready(self) -> bool:
        return self._initialized and self.model is not None

    @property
    def gpu_available(self) -> bool:
        return self.device == "cuda"
