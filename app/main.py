import os
import sys
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

if sys.platform == "win32":
    cuda_bin = os.getenv("CUDA_BIN_PATH", "").strip().strip('"')
    if cuda_bin and os.path.isdir(cuda_bin):
        os.environ["PATH"] = cuda_bin + os.pathsep + os.environ.get("PATH", "")
        os.add_dll_directory(cuda_bin)

from contextlib import asynccontextmanager  # noqa: E402
from typing import Annotated  # noqa: E402
from fastapi import FastAPI, UploadFile, File, HTTPException  # noqa: E402
from fastapi.responses import JSONResponse  # noqa: E402

from app.engine import TranscriptionEngine  # noqa: E402
from app.models import (  # noqa: E402
    TranscriptionMetadata,
    CleanSegment,
    TranscriptionResult,
    SummarizeRequest,
    SummarizeResponse,
    StatusResponse,
)
from app.utils import (  # noqa: E402
    save_upload_to_temp,
    cleanup_temp,
    is_supported_media,
    save_transcription,
    save_summary,
)
from app.services.claude import generate_summary  # noqa: E402


# ─────────────────────────────────────────────────────────────────────────────
# Lifespan
# ─────────────────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Starting Transcription Service...")
    engine = TranscriptionEngine.get_instance()
    print(f"✓ Engine ready: GPU={engine.gpu_available}, Model={engine.model_size}")
    yield
    print("🛑 Shutting down Transcription Service...")


# ─────────────────────────────────────────────────────────────────────────────
# App
# ─────────────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="Transcription Service",
    description="Transcribe video/audio files using Faster-Whisper with GPU acceleration",
    version="3.0.0",
    lifespan=lifespan,
)


# ─────────────────────────────────────────────────────────────────────────────
# Routes
# ─────────────────────────────────────────────────────────────────────────────

@app.get("/", tags=["Health"])
async def root():
    return {
        "name": "Transcription Service",
        "version": "3.0.0",
        "status": "healthy",
        "endpoints": {
            "status": "GET /status",
            "transcribe": "POST /transcribe",
            "summarize": "POST /summarize",
        },
    }


@app.get("/status", response_model=StatusResponse, tags=["Health"])
async def get_status():
    engine = TranscriptionEngine.get_instance()
    return StatusResponse(
        gpu_available=engine.gpu_available,
        device=engine.device,
        model_size=engine.model_size,
        ready=engine.ready,
    )


@app.post("/transcribe", response_model=TranscriptionResult, tags=["Transcription"])
async def transcribe(
    file: Annotated[UploadFile, File(description="Audio or video file to transcribe")],
    language: Annotated[str, "Language code (optional, auto-detect by default)"] = None,
):
    engine = TranscriptionEngine.get_instance()

    if not engine.ready:
        raise HTTPException(status_code=503, detail="Transcription engine is not ready")

    if not is_supported_media(file.filename):
        raise HTTPException(status_code=400, detail=f"Unsupported file format: {file.filename}")

    try:
        temp_path = await save_upload_to_temp(file)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    try:
        date = datetime.now().isoformat(timespec="seconds")
        result = engine.transcribe(temp_path, language=language)
        result["date"] = date
        result["file"] = file.filename

        output_path = save_transcription(result, file.filename)

        metadata = TranscriptionMetadata(
            date=result["date"],
            file=result["file"],
            language=result["language"],
            language_probability=result["language_probability"],
            video_duration_seconds=result["video_duration_seconds"],
            processing_time_seconds=result["processing_time_seconds"],
            speed_factor=result["speed_factor"],
            model=result["model"],
        )
        clean_segments = [
            CleanSegment(
                time=f"{int(seg['start']) // 3600:02d}:{(int(seg['start']) % 3600) // 60:02d}:{int(seg['start']) % 60:02d}",
                text=seg["text"],
            )
            for seg in result["segments"]
        ]

        return TranscriptionResult(
            metadata=metadata,
            full_text=result["text"],
            clean_segments=clean_segments,
            output_file=str(output_path),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")
    finally:
        cleanup_temp(temp_path)


@app.post("/summarize", response_model=SummarizeResponse, tags=["Summary"])
async def summarize(request: SummarizeRequest):
    try:
        summary = await generate_summary(request.transcription)
        output_path = save_summary(summary, request.transcription["metadata"]["file"])
        return SummarizeResponse(summary=summary, output_file=str(output_path))
    except KeyError as e:
        raise HTTPException(status_code=400, detail=f"Missing field in transcription: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Summary generation failed: {str(e)}")


@app.get("/health", tags=["Health"])
async def health_check():
    engine = TranscriptionEngine.get_instance()
    if not engine.ready:
        return JSONResponse(status_code=503, content={"status": "unhealthy", "reason": "Engine not ready"})
    return {"status": "healthy"}


@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    return JSONResponse(status_code=400, content={"detail": str(exc)})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
