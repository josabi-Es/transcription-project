import subprocess
from pathlib import Path

from app.utils import get_output_path

CSS_PATH = Path(__file__).resolve().parents[1] / "assets" / "pdf.css"


def markdown_to_pdf(markdown: str, filename: str) -> tuple[Path, Path]:
    """Save markdown next to its rendered PDF in OUTPUT_DIR, return both paths.

    Uses the same stem as /transcribe, so one recording ends up as
    <stem>.json + <stem>.md + <stem>.pdf. Needs pandoc + wkhtmltopdf on PATH.
    """
    md_path = get_output_path(filename, ".md")
    pdf_path = get_output_path(filename, ".pdf")
    md_path.write_text(markdown, encoding="utf-8")

    # stderr goes straight to the server log, so a pandoc failure is readable there.
    subprocess.run(
        [
            "pandoc", str(md_path), "-o", str(pdf_path),
            "--pdf-engine=wkhtmltopdf",
            "--css", str(CSS_PATH),
            "--metadata", f"title={md_path.stem}",
            # wkhtmltopdf ignores @page margins, so pass them as engine options.
            "--pdf-engine-opt=--margin-top", "--pdf-engine-opt=20mm",
            "--pdf-engine-opt=--margin-bottom", "--pdf-engine-opt=20mm",
            "--pdf-engine-opt=--margin-left", "--pdf-engine-opt=25mm",
            "--pdf-engine-opt=--margin-right", "--pdf-engine-opt=25mm",
            "--pdf-engine-opt=--encoding", "--pdf-engine-opt=utf-8",
        ],
        check=True,
    )
    return md_path, pdf_path
