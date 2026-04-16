# Transcription Service

FastAPI REST service for video/audio transcription using **Faster-Whisper** with automatic GPU acceleration (CUDA).

> 🚀 **Production-Ready**: Built with FastAPI, optimized for NVIDIA GPUs, containerized with Docker.

---

## Architecture

```
┌──────────────────────────────────────┐
│   FastAPI Application                │
│  ├─ POST /transcribe (upload)        │
│  └─ GET /status (service status)     │
└──────────────────────────────────────┘
        ↓
┌──────────────────────────────────────┐
│   Transcription Engine (Singleton)   │
│  ├─ GPU Auto-Detection (CUDA)        │
│  ├─ Faster-Whisper Model             │
│  └─ Load Once, Reuse Across Requests │
└──────────────────────────────────────┘
```

---

## Quick Start

### Option A: Local Development (Work Laptop)

**Requirements:** Python 3.11+, FFmpeg

#### 1. Install uv (if not already installed)
```bash
pip install uv
```

#### 2. Clone and setup
```bash
git clone <your-repo-url>
cd transcription-project
uv sync
```

#### 3. Run development server
```bash
uv run uvicorn app.main:app --reload
```

✅ Server running at `http://localhost:8000`

### Option B: Docker with GPU (Personal Laptop - HP Victus)

**Requirements:** Docker, NVIDIA Docker Runtime, GPU drivers

#### One Command
```bash
docker compose up --build
```

✅ Service available at `http://localhost:8000`

---

## API Endpoints

### GET `/status`
Check if GPU is detected and service is ready.

**Response:**
```json
{
  "gpu_available": true,
  "device": "cuda",
  "model_size": "tiny",
  "ready": true
}
```

### POST `/transcribe`
Upload a video/audio file and get transcription.

**Request:**
```bash
curl -X POST "http://localhost:8000/transcribe" \
  -F "file=@video.mp4" \
  -F "language=es"
```

**Parameters:**
- `file` (required): Audio/video file (mp3, wav, mp4, mkv, etc.)
- `language` (optional): Language code (e.g., 'es', 'en'). Auto-detected if omitted.

**Response:**
```json
{
  "language": "es",
  "language_probability": 0.98,
  "segments": [
    {
      "start": 0.5,
      "end": 3.2,
      "text": "Hola, buenos días."
    }
  ],
  "text": "Hola, buenos días. ¿Cómo estás?"
}
```

### GET `/health`
Simple health check endpoint.

**Response:** `{"status": "healthy"}` (or 503 if unhealthy)

### GET `/` 
Service info.

---

## Configuration

### Environment Variables

Set these in `docker-compose.yml` or via `export`:

| Variable | Default | Description |
|----------|---------|-------------|
| `WHISPER_MODEL` | `tiny` | Model size: `tiny`, `base`, `small`, `medium`, `large-v3` |
| `PYTHONUNBUFFERED` | `1` | Enable real-time logging |

**Example (change to larger model):**
```bash
export WHISPER_MODEL=base
uv run uvicorn app.main:app --reload
```

Or in `docker-compose.yml`:
```yaml
environment:
  - WHISPER_MODEL=base
```

---

## Model Sizes

| Model | Size | Speed | Accuracy | GPU VRAM |
|-------|------|-------|----------|----------|
| `tiny` | 40 MB | ⚡⚡⚡ Fastest | Good | 1 GB |
| `base` | 140 MB | ⚡⚡ | Better | 1.5 GB |
| `small` | 500 MB | ⚡ | Excellent | 2 GB |
| `medium` | 1.5 GB | Medium | Very Good | 5 GB |
| `large-v3` | 3 GB | Slow | Best | 10 GB |

**Default:** `tiny` (recommended for RTX 3050 Ti)

---

## Directory Structure

```
transcription-project/
├── pyproject.toml           # uv configuration with dependencies
├── .python-version          # Python 3.11
├── Dockerfile              # NVIDIA CUDA optimized image
├── docker-compose.yml      # GPU passthrough, volumes, ports
├── README.md               # This file
├── .gitignore              # Exclusions (models, temp files)
└── app/
    ├── __init__.py
    ├── main.py             # FastAPI app, routes, lifespan
    ├── engine.py           # Singleton transcription engine
    └── utils.py            # File upload, temp file handling
```

---

## Development Workflow

### 1. Setup (one-time)
```bash
uv sync
```

### 2. Run with hot-reload
```bash
uv run uvicorn app.main:app --reload
```

### 3. Test with curl
```bash
# Check status
curl http://localhost:8000/status

# Transcribe
curl -X POST "http://localhost:8000/transcribe" \
  -F "file=@test.mp4"
```

### 4. View API docs
```
http://localhost:8000/docs
```

---

## Troubleshooting

### FFmpeg Not Found
```
FileNotFoundError: ffmpeg not found
```

**Solution:**
- **macOS:** `brew install ffmpeg`
- **Ubuntu/Debian:** `sudo apt-get install ffmpeg`
- **Windows (Chocolatey):** `choco install ffmpeg`

### CUDA Not Detected (Docker)
```
ℹ No GPU detected. Using CPU with int8 quantization.
```

**Solution:**
- Verify NVIDIA Docker runtime is installed: `docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi`
- Check NVIDIA drivers: `nvidia-smi`
- Restart Docker daemon

### Out of Memory (GPU)
```
CUDA out of memory
```

**Solutions:**
- Use smaller model: `WHISPER_MODEL=tiny`
- Reduce batch size (not applicable for this service)
- Use CPU mode (slower, but works)

### Model Download Slow
Models are cached in `./models/` after first download. Subsequent runs are instant.

For Docker: use `-v ./models:/app/models` volume (included in `docker-compose.yml`).

---

## Performance Notes

### RTX 3050 Ti Benchmarks
| Model | Per Minute | Notes |
|-------|-----------|-------|
| tiny | 2-3 sec | Verification runs |
| base | 5-8 sec | Recommended default |
| large-v3 | 15-25 sec | Best accuracy |

*Measured with `beam_size=5` (Faster-Whisper optimized)*

---

## Production Deployment

### Using Docker Compose (Recommended)
```bash
docker compose up -d --build
```

### Scale with Additional Instances
For multiple concurrent requests, add GPU workers:
```yaml
services:
  transcriber-1:
    ...
  transcriber-2:
    ...
  transcriber-3:
    ...
```

### Monitoring
```bash
# View logs
docker compose logs -f transcriber

# Check status
curl http://localhost:8000/status

# Health check
curl http://localhost:8000/health
```

---

## Implementation Details

### Singleton Pattern
The `TranscriptionEngine` uses a singleton to load the Whisper model **once** at startup:
- Model is loaded in the FastAPI `lifespan` context manager
- Same instance is reused for all requests
- Eliminates model loading overhead per transcription

### File Handling
- Uploads are saved to `/tmp` (temporary files)
- Automatically cleaned up after transcription
- Original file name extension is preserved

### Hardware Detection
```python
if torch.cuda.is_available():
    device = "cuda"      # Use NVIDIA GPU
    compute_type = "float16"  # Faster, less memory
else:
    device = "cpu"       # Fallback to CPU
    compute_type = "int8"     # Quantized for CPU
```

---

## API Examples

### Python
```python
import requests

response = requests.post(
    "http://localhost:8000/transcribe",
    files={"file": open("video.mp4", "rb")},
    data={"language": "es"}
)

result = response.json()
print(result["text"])
```

### JavaScript/Node.js
```javascript
const formData = new FormData();
formData.append("file", fileInput.files[0]);
formData.append("language", "es");

const response = await fetch(
    "http://localhost:8000/transcribe",
    { method: "POST", body: formData }
);

const result = await response.json();
console.log(result.text);
```

### cURL
```bash
curl -X POST "http://localhost:8000/transcribe" \
  -F "file=@video.mp4" \
  -F "language=es"
```

---

## Docker Compose Reference

**Start service:**
```bash
docker compose up --build
```

**Stop service:**
```bash
docker compose down
```

**View logs:**
```bash
docker compose logs -f transcriber
```

**Remove everything (including volumes):**
```bash
docker compose down -v
```

---

## License

MIT License - Feel free to use for personal or commercial purposes.

---

## Support

- **Documentation:** See this README
- **API Docs:** `http://localhost:8000/docs` (interactive Swagger UI)
- **Health Check:** `curl http://localhost:8000/health`

---

**Ready to transcribe?** 🚀
- **Dev:** Run `uv run uvicorn app.main:app --reload`
- **Production:** Run `docker compose up --build`
