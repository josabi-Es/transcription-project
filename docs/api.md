# API Reference

Interactive docs (try it in the browser) are at `http://localhost:8000/docs` while
the service is running.

---

## GET `/`

Service info and an index of the other endpoints.

---

## GET `/status`

GPU and model state.

```bash
curl http://localhost:8000/status
```

```json
{
  "gpu_available": true,
  "device": "cuda",
  "model_size": "medium",
  "ready": true
}
```

---

## POST `/transcribe`

Upload an audio or video file, get back the full transcription.

```bash
curl -X POST "http://localhost:8000/transcribe?language=es" \
  -F "file=@meeting.mp3"
```

| Field | Where | Required | Description |
|-------|-------|----------|-------------|
| `file` | multipart body | Yes | Audio or video file |
| `language` | query string | No | `es` or `en`. Skips auto-detection, so pass it if you know the language. |

```json
{
  "metadata": {
    "date": "2026-08-13T19:23:03",
    "file": "meeting.mp3",
    "language": "es",
    "language_probability": 0.99,
    "video_duration_seconds": 197.28,
    "processing_time_seconds": 19.5,
    "speed_factor": 10.1,
    "model": "medium"
  },
  "full_text": "Y respecto al Camino de Santiago...",
  "clean_segments": [
    { "time": "00:00:00", "text": "Y respecto al Camino de Santiago..." }
  ],
  "output_file": "storage/output/meeting.json"
}
```

The same payload is also saved to `OUTPUT_DIR/<filename>.json`.

Supported formats. Audio: `.mp3` `.wav` `.m4a` `.flac` `.ogg` `.aac` `.wma`.
Video: `.mp4` `.avi` `.mov` `.mkv` `.webm` `.flv` `.wmv` `.3gp`.

---

## GET `/prompts`

Lists the available formatting prompts (one `.md` file per prompt in `PROMPTS_DIR`).

```bash
curl http://localhost:8000/prompts
```

```json
{ "prompts": ["resumeai", "wordreference"] }
```

---

## POST `/format`

Sends transcribed text through Gemini using one of the prompts above, gets back
polished markdown.

```bash
curl -X POST http://localhost:8000/format \
  -H "Content-Type: application/json" \
  -d '{"text": "...", "prompt_id": "resumeai"}'
```

```json
{ "markdown": "## Traducción\n\n...\n\n## Original\n\n...\n\n## Notas\n\n..." }
```

Rejects text over `FORMAT_MAX_CHARS` (default 50,000) and unknown `prompt_id` values
with a `400`.

---

## POST `/export-pdf`

Renders markdown to a PDF (via pandoc + wkhtmltopdf) and returns the file.

```bash
curl -X POST http://localhost:8000/export-pdf \
  -H "Content-Type: application/json" \
  -d '{"markdown": "## Hello", "filename": "meeting.mp3"}' \
  -o meeting.pdf
```

`filename` just supplies the stem. The response is saved as
`OUTPUT_DIR/<stem>.md` and `OUTPUT_DIR/<stem>.pdf`, and returned as
`application/pdf`.

---

## GET `/health`

```bash
curl http://localhost:8000/health
# {"status": "healthy"}
```

Returns `503` if the Whisper model hasn't finished loading yet.
