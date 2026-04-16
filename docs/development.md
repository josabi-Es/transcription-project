# Local Development (Work Laptop / ThinkPad)

## Setup

```bash
# 1. Install uv (one-time)
pip install uv

# 2. Clone
git clone <your-repo-url>
cd transcription-project

# 3. Configure environment
cp .env.template .env
# Edit .env as needed

# 4. Create virtual environment and install dependencies
uv sync
```

> `uv sync` reads `pyproject.toml` and creates a `.venv` automatically.

---

## Run

```bash
uv run uvicorn app.main:app --reload
```

- Server: `http://localhost:8000`
- Auto-reload on code changes
- Interactive API docs: `http://localhost:8000/docs`

---

## Input / Output Directories

The service reads `INPUT_DIR` and `OUTPUT_DIR` from `.env`:

```
input/
└── interview.mp4        ← place your video here

output/
└── interview.txt        ← transcription saved here automatically
```

On CPU (ThinkPad without GPU), it automatically falls back to `int8` quantization. Slower, but functional for development.

---

## Project Structure

```
transcription-project/
├── pyproject.toml           # uv + project dependencies
├── .python-version          # Python 3.11
├── .env.template            # Copy to .env with your config
├── Dockerfile               # NVIDIA CUDA optimized
├── docker-compose.yml       # GPU passthrough + volumes
├── app/
│   ├── main.py              # FastAPI routes + lifespan
│   ├── engine.py            # WhisperModel singleton
│   └── utils.py             # Upload, temp files, output path
└── docs/
    ├── api.md               # Endpoint reference
    ├── models.md            # Model sizes + VRAM
    ├── docker.md            # Docker deployment guide
    └── development.md       # This file
```

---

## Adding a New Dependency

```bash
uv add <package>
```

This updates `pyproject.toml` and `uv.lock` automatically.

---

## Troubleshooting

**FFmpeg not found:**
- Windows: `choco install ffmpeg` or `winget install FFmpeg`
- macOS: `brew install ffmpeg`
- Linux: `sudo apt-get install ffmpeg`

**CUDA not detected locally:**
- Normal on ThinkPad (no NVIDIA GPU) — falls back to CPU automatically
- On HP Victus: run via Docker (see [docker.md](docker.md))
