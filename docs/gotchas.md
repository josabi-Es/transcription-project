# Gotchas

Failure modes that are easy to hit and not obvious from the error message alone.

## /format returns 400 with an unclear prompt id error

`prompt_id` is the filename of a `.md` file in `prompt/` (without the extension),
picked directly from the dropdown in the UI. The backend validates it against
`^[a-z0-9_-]+$` (`app/services/gemini.py`). Any prompt file with uppercase
letters, spaces, or other characters in its name will list fine in `/prompts`
but fail with a 400 the moment you try to use it.

Fix: name prompt files lowercase, digits, underscores, hyphens only, e.g.
`speech_to_pdf.md`, not `Speech-to-model-PDF.md`.

This has nothing to do with text length or `FORMAT_MAX_CHARS`, even though a
400 there looks similar. Check the response `detail` field to tell them apart.
