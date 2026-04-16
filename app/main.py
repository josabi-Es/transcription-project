"""
FastAPI Application for Video/Audio Transcription
Uses Faster-Whisper with automatic GPU detection.
"""

from contextlib import asynccontextmanager
from typing import Annotated
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.engine import TranscriptionEngine
from app.utils import save_upload_to_temp, cleanup_temp, is_supported_media, save_transcription


# ─────────────────────────────────────────────────────────────────────────────
# Data Models
# ─────────────────────────────────────────────────────────────────────────────

class TranscriptionSegment(BaseModel):
    """A segment of transcribed text with timestamps."""
    start: float
    end: float
    text: str


class TranscriptionResult(BaseModel):
    """Complete transcription result."""
    language: str
    language_probability: float
    segments: list[TranscriptionSegment]
    text: str
    output_file: str | None = None


class StatusResponse(BaseModel):
    """Status of the transcription service."""
    gpu_available: bool
    device: str
    model_size: str
    ready: bool


# ─────────────────────────────────────────────────────────────────────────────
# Lifespan / Startup & Shutdown
# ─────────────────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage app lifecycle.
    Load the transcription engine on startup, cleanup on shutdown.
    """
    # Startup
    print("🚀 Starting Transcription Service...")
    engine = TranscriptionEngine.get_instance()
    print(f"✓ Engine ready: GPU={engine.gpu_available}, Model={engine.model_size}")

    yield

    # Shutdown
    print("🛑 Shutting down Transcription Service...")


# ─────────────────────────────────────────────────────────────────────────────
# FastAPI App
# ─────────────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="Transcription Service",
    description="Transcribe video/audio files using Faster-Whisper with GPU acceleration",
    version="2.0.0",
    lifespan=lifespan
)


# ─────────────────────────────────────────────────────────────────────────────
# Routes
# ─────────────────────────────────────────────────────────────────────────────

@app.get("/", tags=["Health"])
async def root():
    """Service info and health check."""
    return {
        "name": "Transcription Service",
        "version": "2.0.0",
        "status": "healthy",
        "endpoints": {
            "status": "GET /status",
            "transcribe": "POST /transcribe"
        }
    }


@app.get("/status", response_model=StatusResponse, tags=["Health"])
async def get_status():
    """
    Get transcription service status.

    Returns:
        StatusResponse: Current service status including GPU availability and model info
    """
    engine = TranscriptionEngine.get_instance()
    return StatusResponse(
        gpu_available=engine.gpu_available,
        device=engine.device,
        model_size=engine.model_size,
        ready=engine.ready
    )


@app.post("/transcribe", response_model=TranscriptionResult, tags=["Transcription"])
async def transcribe(
    file: Annotated[UploadFile, File(description="Audio or video file to transcribe")],
    language: Annotated[str, "Query parameter for language code (optional, auto-detect by default)"] = None
):
    """
    Transcribe an uploaded video or audio file.

    - **file**: Upload an audio/video file (mp3, wav, mp4, mkv, etc.)
    - **language**: Optional language code (e.g., 'es', 'en'). Auto-detected if not provided.

    Returns:
        TranscriptionResult: Transcription with language, segments, and full text
    """
    engine = TranscriptionEngine.get_instance()

    if not engine.ready:
        raise HTTPException(status_code=503, detail="Transcription engine is not ready")

    # Validate file
    if not is_supported_media(file.filename):
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format: {file.filename}"
        )

    # Save uploaded file to temp
    try:
        temp_path = await save_upload_to_temp(file)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Transcribe
    try:
        result = engine.transcribe(temp_path, language=language)

        # Convert to response model
        segments = [
            TranscriptionSegment(**seg) for seg in result["segments"]
        ]

        # Save transcription to OUTPUT_DIR/<original_name>.txt
        output_path = save_transcription(result["text"], file.filename)

        return TranscriptionResult(
            language=result["language"],
            language_probability=result["language_probability"],
            segments=segments,
            text=result["text"],
            output_file=str(output_path)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")
    finally:
        # Cleanup temp file
        cleanup_temp(temp_path)


@app.get("/health", tags=["Health"])
async def health_check():
    """Simple health check endpoint."""
    engine = TranscriptionEngine.get_instance()
    if not engine.ready:
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "reason": "Engine not ready"}
        )
    return {"status": "healthy"}


# ─────────────────────────────────────────────────────────────────────────────
# Error Handlers
# ─────────────────────────────────────────────────────────────────────────────

@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    """Handle ValueError exceptions."""
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
