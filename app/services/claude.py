import os
from pathlib import Path

import anthropic
import yaml


def _load_prompts() -> dict:
    path = Path(os.getenv("PROMPT_CONFIG_PATH", "app/services/prompts.yaml"))
    return yaml.safe_load(path.read_text(encoding="utf-8"))


async def generate_summary(transcription: dict) -> str:
    prompts = _load_prompts()
    client = anthropic.AsyncAnthropic()

    meta = transcription["metadata"]
    user_content = prompts["summarize"]["user_template"].format(
        file=meta["file"],
        language=meta["language"],
        duration=meta["video_duration_seconds"],
        text=transcription["full_text"],
    )

    async with client.messages.stream(
        model="claude-opus-4-7",
        max_tokens=4096,
        system=[{
            "type": "text",
            "text": prompts["summarize"]["system"],
            "cache_control": {"type": "ephemeral"},
        }],
        messages=[{"role": "user", "content": user_content}],
    ) as stream:
        msg = await stream.get_final_message()

    return msg.content[0].text
