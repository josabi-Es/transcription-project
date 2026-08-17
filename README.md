# Transcriptflow

<p align="center">
  <img src="https://skillicons.dev/icons?i=python,fastapi,pytorch,docker" height="55"/>
</p>

**Have you ever rewatched a two-hour meeting just to find one decision?** Pasting the transcript into a chat AI can work, but only if you already know how to write a good prompt and set up the right context. Most people don't want to learn that just to get a summary.

**Transcriptflow does it for you.** Drop in an audio or video file and it hands back a structured document: key topics, speakers, decisions, in the format you need. No prompt to write, no context to manage. Under the hood, [Faster-Whisper](https://github.com/SYSTRAN/faster-whisper) transcribes the audio locally, with GPU acceleration when available, and the transcript goes through Gemini using ready-made prompt templates (translation, video summary, and more) to produce polished markdown, exportable straight to PDF.

**And it's fast.** With the default `medium` model on a 4 GB GPU, transcription runs at roughly 10x real time: a three-hour recording finishes in about 45 minutes. See your report land almost as fast as you upload the file. Full numbers and model trade-offs are in [`docs/estimate.md`](docs/estimate.md) and [`docs/models.md`](docs/models.md).

https://github.com/user-attachments/assets/5b064803-69ff-439d-8611-47e769be2279

## Documentation

| I want to... | Go to |
|---|---|
| Deploy it with Docker | [`docs/docker.md`](docs/docker.md) |
| Run it locally / hack on it | [`docs/local.md`](docs/local.md) |
| See the API reference | [`docs/api.md`](docs/api.md) |
| Set up environment variables | [`docs/enviroment.md`](docs/enviroment.md) |
| Pick a Whisper model / know how fast it runs | [`docs/models.md`](docs/models.md), [`docs/estimate.md`](docs/estimate.md) |
| Fix a confusing error | [`docs/gotchas.md`](docs/gotchas.md) |
