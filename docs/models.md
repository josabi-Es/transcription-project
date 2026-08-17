# Whisper Models

## Choosing a Model

| Model | Size | Speed | Accuracy | RTX 3050 Ti VRAM |
|-------|------|-------|----------|------------------|
| `tiny` | 40 MB | Fastest | Good | ~1 GB |
| `base` | 140 MB | Fast | Better | ~1.5 GB |
| `small` | 500 MB | Moderate | Excellent | ~2 GB |
| `medium` | 1.5 GB | Medium | Very good | ~3 GB, confirmed running on 4 GB |
| `large-v3` | 3 GB | Slow | Best | ~10 GB |

**Default: `medium`.** Confirmed on an RTX 3050 Ti with 4 GB VRAM at about 10x real
time (a 3-minute recording transcribes in about 20 seconds), with good accuracy on
Spanish. Drop to `small` or `base` only if you're on CPU or VRAM is tight. Go up to
`large-v3` if accuracy matters more than speed and you have more VRAM to spare.

---

## Changing the Model

In `.env`:
```env
WHISPER_MODEL=base
```

That's it. Both the local (`uv run uvicorn ...`) and Docker (`docker compose up`)
paths read it from there.

---

## Model Download

Models are downloaded automatically on first run and cached in `MODELS_DIR`
(default `./storage/models/`). This is mounted as a Docker volume, so models
persist between container restarts.

| Model | Download time (100 Mbps) |
|-------|--------------------------|
| tiny | about 5 sec |
| base | about 15 sec |
| large-v3 | about 4 min |
