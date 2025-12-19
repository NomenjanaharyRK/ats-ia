from pathlib import Path
from pdfminer.high_level import extract_text


class ExtractionError(Exception):
    pass


def extract_cv_text(storage_path: str, mime_type: str) -> str:
    """
    Extraction MVP : ne gère que les PDF texte.
    """
    if mime_type != "application/pdf":
        raise ExtractionError(f"Unsupported mime type: {mime_type}")

    p = Path(storage_path)
    if not p.is_file():
        raise ExtractionError(f"File not found: {storage_path}")

    return extract_text(str(p)) or ""
