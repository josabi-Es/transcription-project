from pydantic import BaseModel


class TranscriptionMetadata(BaseModel):
    date: str
    file: str
    language: str
    language_probability: float
    video_duration_seconds: float
    processing_time_seconds: float
    speed_factor: float
    model: str


class CleanSegment(BaseModel):
    time: str
    text: str


class TranscriptionResult(BaseModel):
    metadata: TranscriptionMetadata
    full_text: str
    clean_segments: list[CleanSegment]
    output_file: str | None = None


class FormatRequest(BaseModel):
    text: str
    prompt_id: str


class FormatResponse(BaseModel):
    markdown: str


class ExportPdfRequest(BaseModel):
    markdown: str
    # Same name used for /transcribe, so all outputs share one stem.
    filename: str = "transcription"


class StatusResponse(BaseModel):
    gpu_available: bool
    device: str
    model_size: str
    ready: bool
