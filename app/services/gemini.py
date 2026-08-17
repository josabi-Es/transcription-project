import os
import re
from pathlib import Path

from google import genai


PROMPT_ID_RE = re.compile(r"^[a-z0-9_-]+$")


def _prompts_dir() -> Path:
    return Path(os.getenv("PROMPTS_DIR", "./prompt"))


def list_prompts() -> list[str]:
    return sorted(p.stem for p in _prompts_dir().glob("*.md"))


def load_prompt(prompt_id: str) -> str:
    if not PROMPT_ID_RE.match(prompt_id):
        raise ValueError(f"Invalid prompt id: {prompt_id!r}")

    path = _prompts_dir() / f"{prompt_id}.md"
    if not path.is_file():
        raise ValueError(f"Unknown prompt {prompt_id!r}. Available: {list_prompts()}")
    return path.read_text(encoding="utf-8")


def max_chars() -> int:
    return int(os.getenv("FORMAT_MAX_CHARS", "50000"))


def format_text(text: str, prompt_id: str) -> str:
    """Reformat a transcription through Gemini using the given prompt."""
    if len(text) > max_chars():
        raise ValueError(f"Text too long: {len(text)} characters, maximum {max_chars()}")

    system_instruction = load_prompt(prompt_id)

    # ponytail: sync call, FastAPI runs the route in a threadpool. Switch to
    # client.aio if concurrent requests ever matter — this is a personal app.
    client = genai.Client()
    interaction = client.interactions.create(
        model=os.getenv("GEMINI_MODEL", "gemini-3.6-flash"),
        system_instruction=system_instruction,
        input=text,
    )
    return interaction.output_text
