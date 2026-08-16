# Docker Deployment

## Requirements

- Docker Engine 24+
- [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html),
  only needed for GPU transcription; the UI container doesn't use a GPU
- NVIDIA GPU drivers on the host

---

## Run

```bash
cp .env.template .env
# edit .env, at minimum set GEMINI_API_KEY
docker compose up --build
```

This starts two containers, built from two separate Dockerfiles under `docker/`:

| Service | What it runs | Built from | GPU | URL |
|---------|--------------|------------|-----|-----|
| `transcriber` | FastAPI backend and Whisper | `docker/backend.Dockerfile` (CUDA base) | Yes | `http://localhost:8000` (docs at `/docs`) |
| `ui` | Streamlit front end | `docker/ui.Dockerfile` (slim, no CUDA) | No | `http://localhost:8501` |

The UI talks to the backend over the compose network (`http://transcriber:8000`),
not through your host, so you never need to set `BACKEND_URL` yourself.

To run in the background:
```bash
docker compose up -d --build
```

---

## Verify GPU is Detected

```bash
docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi
curl http://localhost:8000/status
```

Expected: `{ "gpu_available": true, "device": "cuda", ... }`

---

## Environment Variables

Set in `.env`, loaded via `env_file` in `docker-compose.yml`. Full reference in
`.env.template`; the ones worth knowing up front:

| Variable | Default | Description |
|----------|---------|-------------|
| `BACKEND_PORT` | `8000` | Host port for the backend |
| `UI_PORT` | `8501` | Host port for the UI |
| `WHISPER_MODEL` | `medium` | See [models.md](models.md) |
| `GEMINI_API_KEY` | (none) | Required for `/format` |
| `GEMINI_MODEL` | `gemini-3.6-flash` | Model used to reformat transcriptions |

---

## Volumes

The compose file mounts these from your host into the `transcriber` container:

| Host | Container | Purpose |
|------|-----------|---------|
| `./storage/models` | `/app/storage/models` | Cached Whisper models, avoids re-download |
| `./storage/input` | `/app/storage/input` | Optional scratch space for local files |
| `./storage/output` | `/app/storage/output` | `<stem>.json`, `.md` and `.pdf` per recording |

---

## Useful Commands

```bash
docker compose logs -f transcriber   # backend logs
docker compose logs -f ui            # UI logs
docker compose down                  # stop
docker compose up --build            # rebuild after code changes
docker compose exec transcriber bash # shell into the backend container
```

---

## Troubleshooting

**GPU not detected inside the container:**
```bash
nvidia-ctk --version                 # verify NVIDIA Container Toolkit is installed
sudo systemctl restart docker        # restart after installing
```

**Port already in use:** change `BACKEND_PORT` or `UI_PORT` in `.env`, no need to
edit `docker-compose.yml` directly.
