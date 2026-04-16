# API Reference

Interactive docs available at `http://localhost:8000/docs` when the service is running.

---

## GET `/status`

Returns GPU availability and model state.

```bash
curl http://localhost:8000/status
```

```json
{
  "gpu_available": true,
  "device": "cuda",
  "model_size": "tiny",
  "ready": true
}
```

---

## POST `/transcribe`

Upload a video or audio file and receive a full transcription.

```bash
curl -X POST "http://localhost:8000/transcribe" \
  -F "file=@video.mp4" \
  -F "language=es"
```

**Parameters:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `file` | file | Yes | Audio/video file |
| `language` | string | No | Language code (e.g. `es`, `en`). Auto-detected if omitted. |

**Response:**

```json
{
  "language": "es",
  "language_probability": 0.98,
  "text": "Hola, buenos días. ¿Cómo estás?",
  "output_file": "./output/video.txt",
  "segments": [
    { "start": 0.5, "end": 3.2, "text": "Hola, buenos días." },
    { "start": 3.4, "end": 6.1, "text": "¿Cómo estás?" }
  ]
}
```

> The transcription is also saved automatically to `OUTPUT_DIR/<same_filename>.txt`

---

## GET `/health`

Simple health check. Returns `503` if the engine is not ready.

```bash
curl http://localhost:8000/health
# {"status": "healthy"}
```

---

## Supported Formats

Audio: `.mp3`, `.wav`, `.m4a`, `.flac`, `.ogg`, `.aac`, `.wma`  
Video: `.mp4`, `.avi`, `.mov`, `.mkv`, `.webm`, `.flv`, `.wmv`, `.3gp`
