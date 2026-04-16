# Transcription Project

Transcribe video files to text using **Faster-Whisper** with automatic GPU acceleration (CUDA) detection.

> 🚀 **Fast & Lightweight**: Uses Faster-Whisper (4x faster than OpenAI Whisper) with CTranslate2 optimization.

---

## Quick Start (3 Steps)

### Step 1: Clone the Repository
```bash
git clone https://github.com/yourusername/transcription-project.git
cd transcription-project
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

> **⚠️ First Time Only - Install FFmpeg**
> 
> **Windows:**
> ```bash
> # Using Chocolatey (recommended)
> choco install ffmpeg
> 
> # OR using winget
> winget install FFmpeg
> 
> # OR download from: https://ffmpeg.org/download.html
> ```
> 
> **macOS:**
> ```bash
> brew install ffmpeg
> ```
> 
> **Linux (Ubuntu/Debian):**
> ```bash
> sudo apt-get install ffmpeg
> ```

### Step 3: Run Transcription
```bash
python src/main.py your_video.mp4
```

✅ Done! Transcription will appear in the console.

---

## Features

✅ **Automatic GPU Detection** - Uses CUDA (float16) on GPU, int8 on CPU  
✅ **Multiple Model Sizes** - From tiny (40MB) to large-v3 (3GB)  
✅ **Language Detection** - Automatically detects language in video  
✅ **Output to File** - Save transcriptions as .txt files  
✅ **Timestamps** - Segment-level timestamps included  

---

## Hardware Requirements

### Minimum (CPU Mode)
- Python 3.8+
- 4GB RAM
- Any CPU (slower, but works)

### Recommended (GPU Mode)
- **RTX 3050 Ti** (your HP Victus) ✓
- NVIDIA CUDA 11.8+ compatible GPU
- 6GB+ VRAM (for large-v3 model)
- 16GB+ RAM

---

## Usage Examples

### Basic Transcription (auto-detect language)
```bash
python src/main.py video.mp4
```

### Specify Language
```bash
python src/main.py video.mp4 --language es
```

### Use Different Model Size
```bash
python src/main.py video.mp4 --model base
```

### Save to File
```bash
python src/main.py video.mp4 --output transcription.txt
```

### Combine Options
```bash
python src/main.py video.mp4 --model large-v3 --language en --output output.txt
```

---

## Model Sizes

| Model | Size | Speed | Accuracy | Use Case |
|-------|------|-------|----------|----------|
| `tiny` | 40 MB | ⚡⚡⚡ Fast | Good | Quick verification |
| `base` | 140 MB | ⚡⚡ Medium | Better | Most cases |
| `small` | 500 MB | ⚡ Good | Excellent | High accuracy |
| `medium` | 1.5 GB | Medium | Very Good | Production |
| `large-v3` | 3 GB | Slower | Best | Best accuracy |

**Default:** `tiny` (for fast verification)  
**Change:** Use `--model` flag

---

## Troubleshooting

### FFmpeg Not Found
```
Error: ffmpeg not found
```
**Solution:** Install FFmpeg (see "Quick Start" section)

### Out of Memory (GPU)
```
CUDA out of memory
```
**Solutions:**
- Use a smaller model (`tiny`, `base`)
- Reduce video resolution before transcription
- Use CPU mode (slower but works): models will auto-fallback

### Model Download Slow
Models are downloaded automatically on first run. They're cached in `./models/` for future use.

### CUDA Not Detected
```
ℹ No GPU detected. Using CPU with int8 quantization.
```
- Verify NVIDIA drivers: `nvidia-smi`
- Reinstall PyTorch with CUDA support:
  ```bash
  pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118 --force-reinstall
  ```

---

## Project Structure

```
transcription-project/
├── src/
│   ├── main.py              # Entry point
│   ├── transcriber.py       # Faster-Whisper logic
│   ├── utils.py             # Helper functions
│   └── __init__.py
├── models/                  # Auto-downloaded models (gitignored)
├── requirements.txt         # Python dependencies
├── .gitignore              # Git exclusions
└── README.md               # This file
```

---

## Development on Work Laptop (Optional)

If running on your **ThinkPad** (no GPU), use CPU mode:

```bash
python src/main.py video.mp4
```

It will auto-detect the lack of CUDA and use int8 quantization (slower, but works).

---

## Performance Notes

### RTX 3050 Ti (Your Setup)
- **tiny**: ~2-5 seconds per minute of video
- **base**: ~5-10 seconds per minute
- **large-v3**: ~20-30 seconds per minute

### Estimated Model Sizes & Download Time (First Run)
| Model | Size | Download Time* |
|-------|------|---|
| tiny | 40 MB | ~10 seconds |
| base | 140 MB | ~30 seconds |
| large-v3 | 3 GB | ~5 minutes |

*On a 100 Mbps connection

---

## API Reference

### `transcribe_video(video_path, model_size='tiny', language=None)`

Transcribe a video file.

**Parameters:**
- `video_path` (str): Path to video file
- `model_size` (str): Model to use (default: 'tiny')
- `language` (str, optional): Language code (e.g., 'es', 'en')

**Returns:**
- str: Full transcription text

**Example:**
```python
from src.transcriber import transcribe_video

text = transcribe_video("video.mp4", model_size="base", language="es")
print(text)
```

---

## License

MIT License - Feel free to use this project for personal or commercial purposes.

---

## Questions or Issues?

1. Check the **Troubleshooting** section
2. Verify FFmpeg is installed: `ffmpeg -version`
3. Check GPU driver: `nvidia-smi`
4. Open an issue on GitHub

---

**Ready to transcribe?** Start with Step 1! 🚀
