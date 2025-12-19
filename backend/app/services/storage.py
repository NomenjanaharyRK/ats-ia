from pathlib import Path
import hashlib
from fastapi import UploadFile

BASE_CV_DIR = Path("/app/data/cv_files")

def ensure_base_dir() -> None:
    BASE_CV_DIR.mkdir(parents=True, exist_ok=True)

def save_cv_file_to_disk(file: UploadFile) -> tuple[str, int, str]:
    """
    Retourne (storage_path_str, size_bytes, sha256_hex).
    """
    ensure_base_dir()

    content = file.file.read()
    size_bytes = len(content)
    sha256 = hashlib.sha256(content).hexdigest()

    ext = Path(file.filename).suffix or ""
    filename = f"{sha256}{ext}"
    dest = BASE_CV_DIR / filename
    dest.write_bytes(content)

    # repositionner le pointeur si besoin
    file.file.seek(0)

    return str(dest), size_bytes, sha256
