# Future Improvements

---

## Current Limitations

- Single file upload per request, synchronous processing
- No queue — concurrent requests block each other
- Model loaded once at startup, no dynamic switching
- No post-processing on the raw transcript

---

## Short Term

### Async job queue
Large files (2–3h) block the API until done. A simple queue (Celery + Redis, or just `asyncio.Queue`) would allow submitting a job and polling for results, making the service usable in production workflows.

```
POST /transcribe      → returns job_id
GET  /jobs/{job_id}   → returns status + result when done
```

### Batch endpoint
For HR use cases processing many recordings per day, a batch endpoint avoids re-uploading files one by one and lets the service prioritize the queue.

### VAD pre-processing
Run a lightweight Voice Activity Detection pass before transcription to strip silence and irrelevant audio. Reduces model input size significantly on meeting recordings and interviews. `silero-vad` integrates well with Faster-Whisper.

---

## Model Strategy

### large-v3 on GPU (when available)
For daily HR analytics work, `large-v3` is the right model — best accuracy on Spanish, handles accents, crosstalk, and domain vocabulary significantly better than `medium`. On the RTX 3050 Ti it works but sits at the VRAM limit; on a dedicated GPU (A10G, T4) it runs comfortably.

### Distil-Whisper
`distil-large-v3` is a distilled version of `large-v3`: ~6x faster, ~49% fewer parameters, accuracy within 1% WER on most benchmarks. Good middle ground if `large-v3` is too slow and `medium` is not accurate enough.

```
WHISPER_MODEL=distil-large-v3
```

### Dynamic model selection
Different content types warrant different models. A 5-min clip can use `small`; a 3h interview warrants `large-v3`. This could be exposed as a request parameter or auto-selected based on file duration.

---

## Cloud & Cost Optimization

### When to move to cloud

| Daily volume | Recommendation |
|---|---|
| < 2h audio/day | Local GPU (current setup) |
| 2–8h audio/day | Local GPU + queue |
| > 8h audio/day | Cloud GPU on demand |
| Burst workloads | Spot/preemptible instances |

### Azure options (cost-ordered)

| Option | GPU | Approx. cost | Best for |
|---|---|---|---|
| **NC4as T4 v3** | T4 16GB | ~$0.50/h | Daily processing, `large-v3` |
| **NC6s v3** | V100 16GB | ~$2.50/h | Heavy batch |
| **Container Apps** | Serverless | Pay per use | Sporadic workloads |

**Recommended pattern**: spin up a spot VM, process the day's batch, shut it down. At ~$0.50/h, 4h of audio with `large-v3` costs under $1.

### Self-hosted alternative
A used A10G or RTX 3090 (24GB VRAM) runs `large-v3` at ~8x real-time. One-time hardware cost amortizes quickly for teams processing audio daily.

---

## HR / People Analytics Use Cases

### Speaker diarization
Identify who speaks when. Combines Faster-Whisper with `pyannote-audio`:
- Output: timestamped transcript per speaker
- Useful for: interview analysis, meeting minutes, performance reviews

### Post-processing pipeline
Raw Whisper output benefits from:
1. **Punctuation restoration** — `deepmultilingualpunctuation` or a fine-tuned model
2. **Named entity recognition** — extract names, roles, companies from transcripts
3. **Summarization** — LLM pass (GPT-4o, Claude) to produce structured summaries
4. **Sentiment / tone analysis** — useful for HR interview scoring

### Fine-tuning on domain vocabulary
If transcriptions consistently mishandle company names, HR terminology, or internal acronyms, fine-tuning `medium` or `large-v3` on a small labeled dataset (50–100 examples) can bring WER down significantly. Faster-Whisper supports loading fine-tuned CTranslate2 models directly.

---

## Deployment

### Docker on cloud (current Dockerfile is ready)
The existing Dockerfile works as-is on any NVIDIA-enabled cloud instance. Only change needed: set `WHISPER_DEVICE=gpu` and `WHISPER_MODEL=large-v3` in the cloud `.env`.

### Kubernetes / AKS
For teams: deploy as a Kubernetes service with GPU node pools. HPA (Horizontal Pod Autoscaler) can scale based on queue depth.

### Model caching
In cloud deployments, pre-download the model into the container image or a shared volume to avoid the HuggingFace download on every cold start.

```dockerfile
RUN uv run python -c "from faster_whisper import WhisperModel; WhisperModel('large-v3', download_root='/app/models')"
```
