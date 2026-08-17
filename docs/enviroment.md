# Environment Variables

All variables are read from a `.env` file at the project root. Copy
[`.env.template`](../.env.template) to `.env` and adjust the values you need;
everything else can keep its default.

```bash
cp .env.template .env
```

---

## Ports

| Variable | Default | Description |
|----------|---------|-------------|
| `BACKEND_PORT` | `8000` | Host port for the FastAPI backend |
| `UI_PORT` | `8501` | Host port for the Streamlit UI |

---

## Whisper

| Variable | Default | Description |
|----------|---------|-------------|
| `WHISPER_MODEL` | `medium` | `tiny`, `base`, `small`, `medium`, or `large-v3`. Bigger models are slower but more accurate. See [`models.md`](models.md) |
| `WHISPER_DEVICE` | `gpu` | `gpu`, `cpu`, or `auto`. `gpu` fails without a working CUDA setup |
| `CUDA_BIN_PATH` | (empty) | Windows only. Path to the CUDA Toolkit `bin` folder, only needed if it isn't already on `PATH` |
| `MODELS_DIR` | `./storage/models` | Where downloaded Whisper models are cached |
| `OUTPUT_DIR` | `./storage/output` | Where transcription and export files are saved |
| `WHISPER_BEAM_SIZE` | `3` | Beam search width. `1` is fastest, `3` is balanced, `5` favors quality |
| `WHISPER_VAD_FILTER` | `true` | Skips silent sections automatically, speeds up long recordings |
| `WHISPER_CONDITION_ON_PREVIOUS_TEXT` | `true` | Uses the previous segment as context for the next one |
| `WHISPER_INITIAL_PROMPT` | (empty) | Optional text hint to steer transcription style or vocabulary |

---

## Gemini

Used by the `/format` endpoint to turn a raw transcript into structured
markdown.

| Variable | Default | Description |
|----------|---------|-------------|
| `GEMINI_API_KEY` | (empty, required) | Get a key at [aistudio.google.com/apikey](https://aistudio.google.com/apikey). This is the exact variable name the `google-genai` SDK reads by default |
| `GEMINI_MODEL` | `gemini-3.6-flash` | Model used to reformat transcriptions |
| `PROMPTS_DIR` | `./prompt` | Folder holding the formatting prompt templates, one `.md` file per prompt |
| `FORMAT_MAX_CHARS` | `50000` | Maximum input size for `/format`. Gemini's output limit is 65,536 tokens (about 195,000 characters), and the bilingual prompt template produces roughly 2.1x the input length, so keep this well under ~90,000 |

---

For running with Docker, these same variables are loaded through `env_file`
in `docker-compose.yml`, see [`docker.md`](docker.md).
