"""
Service d'extraction de texte à partir de CV (PDF, DOCX, images).

Améliorations :
- Utilisation de Tesseract en français (lang="fra") pour les CV FR.
- OCR des PDF scannés en haute résolution (dpi=300).
- Pré-traitement des images (contraste, binarisation, réduction de bruit)
  pour améliorer la qualité de l'OCR sur PNG/JPG/TIFF.
- Calcul d'un score de qualité simple basé sur la densité de texte.
"""

from pathlib import Path
from typing import Tuple, Dict, Any

from pdfminer.high_level import extract_text as pdfminer_extract_text
from docx import Document
from pdf2image import convert_from_path
from PIL import Image
import pytesseract

# Pré-traitement des images pour Tesseract
import cv2
import numpy as np


class ExtractionError(Exception):
    """Exception spécifique à l'extraction de CV."""
    pass


# ---------------------------------------------------------------------------
# Fonctions d'extraction PDF texte / DOCX
# ---------------------------------------------------------------------------

def _extract_pdf_text_native(path: Path) -> str:
    """
    Extraction de texte pour les PDF 'natifs' (non scannés).

    Utilise pdfminer pour lire le texte directement.
    Si une erreur survient, lève ExtractionError.
    """
    try:
        text = pdfminer_extract_text(str(path))
    except Exception as e:
        raise ExtractionError(f"Error extracting text from PDF: {e}") from e
    return text or ""


def _extract_docx_text(path: Path) -> str:
    """
    Extraction de texte pour les fichiers .docx.

    Parcourt les paragraphes du document et les concatène
    avec des sauts de ligne.
    """
    try:
        doc = Document(str(path))
    except Exception as e:
        raise ExtractionError(f"Error opening DOCX: {e}") from e

    return "\n".join(p.text for p in doc.paragraphs)


# ---------------------------------------------------------------------------
# Pré-traitement et OCR avec Tesseract
# ---------------------------------------------------------------------------

def _preprocess_for_ocr(pil_img: Image.Image) -> Image.Image:
    """
    Améliore l'image pour l'OCR.

    Étapes :
    - Conversion en niveaux de gris.
    - Égalisation d'histogramme (augmentation du contraste).
    - Binarisation (Otsu).
    - Réduction légère du bruit par médiane.
    """
    # PIL -> tableau numpy (OpenCV travaille sur des arrays)
    img = np.array(pil_img)

    # Si l'image est en couleur, on la convertit en niveaux de gris.
    if len(img.shape) == 3:  # H x W x C
        img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

    # Augmenter le contraste
    img = cv2.equalizeHist(img)

    # Binarisation automatique (Otsu)
    _, img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Réduction de bruit légère
    img = cv2.medianBlur(img, 3)

    # Retour en image PIL
    return Image.fromarray(img)


def _ocr_image(img: Image.Image) -> str:
    """
    OCR avec Tesseract sur une image PIL.

    - Pré-traitement de l'image.
    - Utilisation de la langue française.
    - Mode de segmentation adapté à une page de texte.
    """
    img = _preprocess_for_ocr(img)
    return pytesseract.image_to_string(img, lang="fra", config="--psm 3")


# ---------------------------------------------------------------------------
# PDF scannés et images disque
# ---------------------------------------------------------------------------

def _extract_pdf_text_ocr(path: Path) -> str:
    """
    Extraction OCR pour les PDF scannés :
    - Conversion de chaque page en image (pdf2image, dpi=300).
    - Pré-traitement + OCR avec Tesseract sur chaque page.
    - Concaténation des textes.
    """
    try:
        pages = convert_from_path(str(path), dpi=300)
    except Exception as e:
        raise ExtractionError(f"Error converting PDF to images: {e}") from e

    texts: list[str] = []
    for page in pages:
        texts.append(_ocr_image(page))
    return "\n".join(texts)


def _extract_image_file(path: Path) -> str:
    """
    Extraction de texte pour les images (jpg, png, tiff, ...).

    - Ouverture de l'image avec PIL.
    - Pré-traitement.
    - OCR via Tesseract.
    """
    try:
        img = Image.open(str(path))
    except Exception as e:
        raise ExtractionError(f"Error opening image: {e}") from e

    return _ocr_image(img)


# ---------------------------------------------------------------------------
# Score de qualité
# ---------------------------------------------------------------------------

def _compute_quality_score(text: str, file_size: int) -> float:
    """
    Heuristique simple de qualité d'extraction.

    - Plus il y a de texte par octet de fichier, meilleur est le score.
    - Résultat borné entre 0.0 et 1.0.
    """
    n_chars = len(text.strip())
    if file_size <= 0:
        return 0.0

    ratio = n_chars / file_size  # chars par octet
    score = ratio * 10.0         # facteur arbitraire

    if score > 1.0:
        score = 1.0
    if score < 0.0:
        score = 0.0
    return score


# ---------------------------------------------------------------------------
# Pipeline principal
# ---------------------------------------------------------------------------

def extract_cv_text(
    storage_path: str,
    mime_type: str,
) -> Tuple[str, float, Dict[str, Any]]:
    """
    Pipeline principal d'extraction de texte pour un CV.

    - Gère :
      * PDF texte (pdfminer)
      * PDF scannés (OCR via pdf2image + Tesseract)
      * DOCX
      * Images (PNG/JPG/TIFF via Tesseract + pré-traitement)
      * Fallback en texte brut
    - Renvoie (text, quality_score, meta)
    """
    path = Path(storage_path)
    if not path.is_file():
        raise ExtractionError(f"File not found: {storage_path}")

    suffix = path.suffix.lower()
    text: str = ""

    # 1) PDF (texte ou scanné)
    if mime_type == "application/pdf" or suffix == ".pdf":
        text = _extract_pdf_text_native(path)
        if len(text.strip()) < 200:
            text = _extract_pdf_text_ocr(path)

    # 2) DOCX
    elif mime_type in {
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    } or suffix == ".docx":
        text = _extract_docx_text(path)

    # 3) Images (PNG, JPG, TIFF, ...)
    elif mime_type in {
        "image/png",
        "image/jpeg",
        "image/jpg",
        "image/tiff",
    } or suffix in {".png", ".jpg", ".jpeg", ".tif", ".tiff"}:
        text = _extract_image_file(path)

    # 4) Fallback : tentative de lecture en texte brut
    else:
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except Exception as e:
            raise ExtractionError(
                f"Unsupported mime type and cannot read as text: {mime_type}"
            ) from e

    quality = _compute_quality_score(text, path.stat().st_size)
    meta: Dict[str, Any] = {
        "file_ext": suffix,
        "mime_type": mime_type,
        "n_chars": len(text),
        "quality_score": quality,
    }
    return text, quality, meta
