# Transcription Service

FastAPI REST service for video/audio transcription using **Faster-Whisper** with automatic GPU acceleration (CUDA).

---

## Quick Start

### Option A — Local Dev (ThinkPad / no GPU)

> Requirements: Python 3.11+, FFmpeg, [uv](https://github.com/astral-sh/uv)

```bash
git clone <your-repo-url> && cd transcription-project
cp .env.template .env
uv sync
uv run uvicorn app.main:app --reload
```

### Option B — Docker with GPU (HP Victus / RTX 3050 Ti)

> Requirements: Docker, [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html)

```bash
git clone <your-repo-url> && cd transcription-project
cp .env.template .env
docker compose up --build
```

Service available at `http://localhost:8000`  
Interactive API docs at `http://localhost:8000/docs`

---

## Usage

Place your video in `./input/`, then upload via API:

```bash
curl -X POST "http://localhost:8000/transcribe" \
  -F "file=@input/video.mp4"
```

The transcription is saved automatically to `./output/video.txt`.

---

## Configuration

Copy `.env.template` to `.env` and adjust:

| Variable | Default | Description |
|----------|---------|-------------|
| `WHISPER_MODEL` | `tiny` | `tiny` \| `base` \| `small` \| `medium` \| `large-v3` |
| `INPUT_DIR` | `./input` | Directory with your video/audio files |
| `OUTPUT_DIR` | `./output` | Where `.txt` transcriptions are saved |

---

## Documentation

| Doc | Description |
|-----|-------------|
| [docs/api.md](docs/api.md) | API endpoints reference |
| [docs/models.md](docs/models.md) | Model sizes, VRAM, accuracy |
| [docs/docker.md](docs/docker.md) | Docker + GPU setup |
| [docs/development.md](docs/development.md) | Local dev workflow |
