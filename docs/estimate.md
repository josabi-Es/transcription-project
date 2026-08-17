# Transcription Time Estimates & Inference Hyperparameters

Reference GPU: **NVIDIA GeForce RTX 3050 Ti Laptop (4 GB VRAM)**

---

## Model Estimates

| Model | VRAM | Speed (GPU) | Speed (CPU) | ES Accuracy |
|-------|------|-------------|-------------|-------------|
| `tiny` | ~250 MB | ~30x | ~4x | Poor |
| `base` | ~500 MB | ~15x | ~2x | Fair |
| `small` | ~1 GB | ~8x | ~1x | Good |
| `medium` | ~2.5 GB | ~4x | 0.3x | Very Good |
| `large-v3` | ~4 GB | ~1.5x | Not recommended | Excellent |

> `large-v3` is right at the 4 GB VRAM limit. Risk of OOM on long audio.

---

## Duration Estimates (`medium` model, confirmed ~1 min on GPU)

| Video Duration | Estimated Time (GPU) |
|----------------|----------------------|
| 5 min | ~1–2 min |
| 30 min | ~7–8 min |
| 1 hour | ~15 min |
| 2 hours | ~30 min |
| 3 hours | ~45 min |

---

## Inference Hyperparameters

Whisper is an encoder-decoder transformer. Its inference hyperparameters directly control the decoding strategy and quality/speed trade-off.

### Currently hardcoded in `engine.py`

| Parameter | Current value | Effect |
|-----------|--------------|--------|
| `beam_size` | `5` | Beam search width. Higher = more accurate, slower. Range: 1–10 |

### Key parameters available in Faster-Whisper

| Parameter | Default | Description |
|-----------|---------|-------------|
| `beam_size` | `5` | Beam search candidates. `1` = greedy (fastest). `5`–`10` for best quality |
| `temperature` | `0` | Sampling temperature. `0` = deterministic. Higher = more creative/random |
| `vad_filter` | `False` | Voice Activity Detection: skips silence automatically. Speeds up long videos significantly |
| `condition_on_previous_text` | `True` | Uses prior segment as context. Helps coherence but can propagate errors |
| `compression_ratio_threshold` | `2.4` | Discards segments with too much repetition (hallucination filter) |
| `log_prob_threshold` | `-1.0` | Discards low-confidence segments |
| `no_speech_threshold` | `0.6` | Probability above which a segment is treated as silence |
| `patience` | `1.0` | Beam search patience. Higher = considers more candidates |
| `length_penalty` | `1.0` | Penalizes shorter or longer outputs |

### Recommended settings by use case

| Use case | `beam_size` | `vad_filter` | `temperature` |
|----------|-------------|--------------|---------------|
| Fast draft | `1` | `True` | `0` |
| Balanced (default) | `5` | `False` | `0` |
| Max accuracy | `10` | `False` | `0` |
| Long video with silence | `5` | `True` | `0` |

### What affects real transcription time

- **Silence**: with `vad_filter=True`, Faster-Whisper skips non-speech, a big speedup on long videos
- **`beam_size`**: going from 5 → 1 is roughly 2x faster with some accuracy loss
- **Speech density**: fast-paced podcasts take longer than slow presentations
- **Explicit language**: passing `?language=es` skips auto-detection, saves time on long audio
