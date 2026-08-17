"""Streamlit front-end. Talks to the FastAPI backend over HTTP, holds no logic.

Single-flow UI: upload + pick a prompt + one button runs the whole
transcribe -> format -> export-pdf pipeline, stopping at the first failure.
"""

import os

import httpx
import streamlit as st
from dotenv import load_dotenv

from app.utils.files import SUPPORTED_FORMATS

load_dotenv()

# Locked to ES/EN: the formatting prompt is bilingual ES<->EN only, so letting
# Whisper auto-detect a third language would break it downstream.
LANGUAGES = {"Español": "es", "English": "en"}

BACKEND = os.getenv("BACKEND_URL", f"http://localhost:{os.getenv('BACKEND_PORT', '8000')}")
# Whisper and Gemini both take tens of seconds. httpx defaults to 5s, which
# would fail every single call.
TIMEOUT = httpx.Timeout(600.0, connect=10.0)

st.set_page_config(page_title="Transcriflow", page_icon="📜", layout="centered")

st.markdown(
    """
    <style>
    .stApp {
        background-color: #f6f3ec;
        background-image:
            radial-gradient(circle at 1px 1px, rgba(31,56,100,0.08) 1px, transparent 0);
        background-size: 22px 22px;
    }
    h1 {
        font-family: Georgia, "Times New Roman", serif;
        color: #1f3864;
        margin-bottom: 0;
    }
    .subtitle {
        color: #5a6b8c;
        font-size: 0.95rem;
        margin-bottom: 1.6rem;
    }
    div[data-testid="stFileUploaderDropzone"] {
        background-color: #ffffffcc;
        border: 1px dashed #a6b1c2;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("📜 Transcriflow")
st.markdown('<p class="subtitle">Audio o vídeo → markdown bilingüe → PDF</p>', unsafe_allow_html=True)


def call(method: str, path: str, **kwargs) -> dict | bytes | None:
    """Call the backend; on failure show the server's error detail and return None."""
    try:
        r = httpx.request(method, f"{BACKEND}{path}", timeout=TIMEOUT, **kwargs)
    except httpx.HTTPError as e:
        st.error(f"No se pudo contactar con el backend ({BACKEND}): {e}")
        return None

    if r.status_code != 200:
        try:
            detail = r.json().get("detail", r.text)
        except ValueError:
            detail = r.text
        st.error(f"**{path}** falló ({r.status_code}): {detail}")
        return None

    ct = r.headers.get("content-type", "")
    return r.json() if ct.startswith("application/json") else r.content


# ── Source ──────────────────────────────────────────────────────────────────
uploaded = st.file_uploader(
    "Audio o vídeo",
    type=[fmt.lstrip(".") for fmt in sorted(SUPPORTED_FORMATS)],
)

if uploaded and st.session_state.get("filename") != uploaded.name:
    st.session_state.clear()
    st.session_state["filename"] = uploaded.name

language_label = st.selectbox("Idioma del audio", list(LANGUAGES))
language = LANGUAGES[language_label]

try:
    prompts_resp = httpx.get(f"{BACKEND}/prompts", timeout=5.0)
except httpx.HTTPError:
    st.error(f"Backend no disponible ({BACKEND}). Arráncalo y recarga la página.")
    st.stop()
prompts = prompts_resp.json()["prompts"] if prompts_resp.status_code == 200 else []
if not prompts:
    st.warning("No hay prompts en el backend. Añade un .md en la carpeta configurada por PROMPTS_DIR.")
prompt_id = st.selectbox("Prompt de formateo", prompts, disabled=not prompts)

generate = st.button(
    "Generar documento",
    type="primary",
    disabled=uploaded is None or not prompt_id,
)

# ── Pipeline ─────────────────────────────────────────────────────────────────
if generate:
    st.session_state.pop("markdown", None)
    st.session_state.pop("pdf", None)

    with st.status("Generando documento...", expanded=True) as status:
        st.write(f"Transcribiendo con Whisper ({language_label})...")
        transcription = call(
            "POST", "/transcribe",
            params={"language": language},
            files={"file": (uploaded.name, uploaded.getvalue())},
        )
        if transcription is None:
            status.update(label="Fallo en la transcripción", state="error")
            st.stop()

        meta = transcription["metadata"]
        st.write(
            f"✓ {meta['language']} · {meta['video_duration_seconds']:.0f}s de audio "
            f"· {len(transcription['full_text'])} caracteres"
        )

        st.write(f"Formateando con Gemini ({prompt_id})...")
        markdown = call(
            "POST", "/format",
            json={"text": transcription["full_text"], "prompt_id": prompt_id},
        )
        if markdown is None:
            status.update(label="Fallo al formatear", state="error")
            st.stop()
        markdown = markdown["markdown"]
        st.write(f"✓ {len(markdown)} caracteres de markdown")

        st.write("Generando PDF...")
        pdf = call(
            "POST", "/export-pdf",
            json={"markdown": markdown, "filename": st.session_state["filename"]},
        )
        if pdf is None:
            status.update(label="Fallo al generar el PDF", state="error")
            st.stop()
        st.write("✓ PDF listo")

        status.update(label="Documento generado", state="complete")

    st.session_state["markdown"] = markdown
    st.session_state["pdf"] = pdf

# ── Results ────────────────────────────────────────────────────────────────
if "markdown" in st.session_state:
    with st.expander("Vista previa", expanded=True):
        st.markdown(st.session_state["markdown"])

    stem = st.session_state["filename"].rsplit(".", 1)[0]
    st.download_button(
        "⬇️ Descargar PDF",
        st.session_state["pdf"],
        file_name=f"{stem}.pdf",
        mime="application/pdf",
        type="primary",
    )
