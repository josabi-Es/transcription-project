# Local Development

## Setup

```bash
# 1. Install uv (one-time)
pip install uv

# 2. Clone
git clone <your-repo-url>
cd transcription-project

# 3. Configure environment
cp .env.template .env
# edit .env, at minimum set GEMINI_API_KEY

# 4. Create the virtual environment and install dependencies
uv sync --all-extras
```

`uv sync` reads `pyproject.toml` and creates `.venv` automatically. Backend
and UI dependencies are split into separate extras (`backend`, `ui`) so each
Docker image only installs what it needs — `--all-extras` installs both,
since locally you run both processes from the same `.venv`.

---

## Run

Two processes, two terminals. The UI just talks HTTP to the backend, it has no
logic of its own.

```bash
# Terminal 1: backend
uv run uvicorn app.main:app --reload
```

```bash
# Terminal 2: UI
uv run streamlit run app/streamlit.py
```

- Backend: `http://localhost:8000` (interactive docs at `/docs`)
- UI: `http://localhost:8501`

---

## Project Structure

```
transcription-project/
├── pyproject.toml           # uv + project dependencies
├── .env.template            # copy to .env with your config
├── docker-compose.yml       # backend (GPU) and UI (no GPU), separate images
├── docker/
│   ├── backend.Dockerfile    # CUDA base, FastAPI + Whisper
│   └── ui.Dockerfile         # slim base, Streamlit only
├── app/
│   ├── main.py               # FastAPI routes and lifespan
│   ├── streamlit.py          # "Transcripta" UI
│   ├── engine/whisper.py     # WhisperModel singleton
│   ├── models/schemas.py     # request/response models
│   ├── services/gemini.py    # /format, calls Gemini with a prompt
│   ├── services/pdf.py       # /export-pdf, pandoc + wkhtmltopdf
│   └── utils/files.py        # upload handling, temp files, output paths
├── prompt/                   # one .md per formatting prompt (filename = prompt_id)
└── storage/
    ├── models/                # cached Whisper models
    ├── input/                 # optional scratch space for local files
    └── output/                # <stem>.json / .md / .pdf per processed recording
```

---

## PDF export prerequisites (Windows)

`POST /export-pdf` shells out to pandoc, which uses wkhtmltopdf as its PDF engine.
Neither is a Python dependency, so install both yourself and make sure they're on
the `PATH`. Docker installs the same versions automatically (see
[docker.md](docker.md)); this section is only for running the backend directly.

### 1. Pandoc

- Version: 3.10.2
- Download: <https://github.com/jgm/pandoc/releases/tag/3.10.2>, get
  `pandoc-3.10.2-windows-x86_64.msi` (about 39.5 MB)
- Install: run the `.msi`, next-next-finish. It adds itself to the `PATH`.

### 2. wkhtmltopdf

- Version: 0.12.6
- Download: <https://wkhtmltopdf.org/downloads.html>, choose Windows, then
  Installer (Vista or later), 64-bit
- Install: run the installer.
- It doesn't always add itself to the `PATH`. Verify below and add
  `C:\Program Files\wkhtmltopdf\bin` yourself if needed.

### 3. Verify

```powershell
pandoc --version
wkhtmltopdf --version
```

Both must print a version. Then check the pair actually works together:

```powershell
pandoc storage/output/example.md -o example.pdf --pdf-engine=wkhtmltopdf
```

If `wkhtmltopdf` won't land on the `PATH`, pass its full path instead:
`--pdf-engine="C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe"`.

---

## Adding a New Dependency

```bash
uv add <package>
```

Updates `pyproject.toml` and `uv.lock` automatically.

---

## Troubleshooting

**FFmpeg not found:**
- Windows: `choco install ffmpeg` or `winget install FFmpeg`
- macOS: `brew install ffmpeg`
- Linux: `sudo apt-get install ffmpeg`

**CUDA not detected locally:**
- Normal on a machine with no NVIDIA GPU, it falls back to CPU automatically
  (`WHISPER_DEVICE=auto` in `.env`).
- On a GPU machine, double-check `CUDA_BIN_PATH` in `.env` if the DLLs aren't
  already on the system `PATH`.
