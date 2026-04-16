# Whisper Models

## Choosing a Model

| Model | Size | Speed | Accuracy | RTX 3050 Ti VRAM |
|-------|------|-------|----------|------------------|
| `tiny` | 40 MB | ⚡⚡⚡ | Good | ~1 GB |
| `base` | 140 MB | ⚡⚡ | Better | ~1.5 GB |
| `small` | 500 MB | ⚡ | Excellent | ~2 GB |
| `medium` | 1.5 GB | Medium | Very good | ~5 GB |
| `large-v3` | 3 GB | Slow | Best | ~10 GB |

**Recommendation for RTX 3050 Ti (4 GB VRAM):** `tiny` or `base`

---

## Changing the Model

In `.env`:
```env
WHISPER_MODEL=base
```

Or at runtime (local dev):
```bash
WHISPER_MODEL=base uv run uvicorn app.main:app --reload
```

Or in `docker-compose.yml`:
```yaml
environment:
  - WHISPER_MODEL=base
```

---

## Model Download

Models are downloaded automatically on first run and cached in `./models/`.  
This folder is mounted as a Docker volume so they persist between container restarts.

| Model | Download time (100 Mbps) |
|-------|--------------------------|
| tiny | ~5 sec |
| base | ~15 sec |
| large-v3 | ~4 min |
