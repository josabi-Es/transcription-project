# Docker Deployment

## Requirements

- Docker Engine 24+
- [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html)
- NVIDIA GPU drivers installed on the host

---

## Run (HP Victus with RTX 3050 Ti)

```bash
docker compose up --build
```

Service will be available at `http://localhost:8000`.

To run in background:
```bash
docker compose up -d --build
```

---

## Verify GPU is Detected

```bash
# Check NVIDIA runtime works
docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi

# Check the service detects GPU
curl http://localhost:8000/status
```

Expected:
```json
{ "gpu_available": true, "device": "cuda", ... }
```

---

## Environment Variables

Set in `docker-compose.yml` under `environment:`:

| Variable | Default | Description |
|----------|---------|-------------|
| `WHISPER_MODEL` | `tiny` | Model size (see [models.md](models.md)) |
| `INPUT_DIR` | `./input` | Directory with videos to transcribe |
| `OUTPUT_DIR` | `./output` | Directory where `.txt` files are saved |

---

## Volumes

The compose file mounts these directories from your host into the container:

| Host | Container | Purpose |
|------|-----------|---------|
| `./models` | `/app/models` | Cached Whisper models (avoids re-download) |
| `./input` | `/app/input` | Input video/audio files |
| `./output` | `/app/output` | Output transcription files |

---

## Useful Commands

```bash
# View logs
docker compose logs -f transcriber

# Stop
docker compose down

# Rebuild after code changes
docker compose up --build

# Enter container shell
docker compose exec transcriber bash
```

---

## Troubleshooting

**GPU not detected inside container:**
```bash
# Verify NVIDIA Container Toolkit is installed
nvidia-ctk --version

# Restart Docker daemon after installing
sudo systemctl restart docker
```

**Port already in use:**
```yaml
# Change port in docker-compose.yml
ports:
  - "8001:8000"   # host:container
```
