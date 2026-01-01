from celery import shared_task
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.cv_file import CVFile, CVFileStatus
from app.models.cv_text import CVText
from app.services.cv_extraction import extract_cv_text, ExtractionError


@shared_task(name="app.workers.tasks.process_cv_file")
def process_cv_file(cv_file_id: int) -> None:
    """
    Tâche Celery qui :
    - récupère un CVFile et son CVText associé,
    - lance l'extraction de texte,
    - met à jour les statuts et stocke le texte + quality_score.
    """
    print("### PROCESS_CV_FILE START, ID =", cv_file_id)

    db: Session = SessionLocal()
    try:
        # 1. Charger le fichier CV
        cv_file: CVFile | None = db.get(CVFile, cv_file_id)
        if not cv_file:
            print("### NO CV_FILE FOUND FOR ID", cv_file_id)
            return

        # 2. Marquer le fichier comme en cours d'extraction
        cv_file.status = CVFileStatus.EXTRACTING.value
        db.flush()

        # 3. Récupérer la ligne CVText associée à la candidature
        cv_text: CVText | None = (
            db.query(CVText)
            .filter(CVText.application_id == cv_file.application_id)
            .one_or_none()
        )
        if not cv_text:
            cv_file.status = CVFileStatus.FAILED.value
            cv_file.error_message = "No CVText row for this application"
            db.commit()
            print("### NO CV_TEXT FOR APPLICATION", cv_file.application_id)
            return

        # 4. Extraction de texte + debug OCR
        try:
            # Appel OCR / extraction
            result = extract_cv_text(cv_file.storage_path, cv_file.mime_type)

            # Déballer le résultat
            if isinstance(result, tuple):
                extracted_text = result[0]
                quality_score = result[1] if len(result) > 1 else None
                meta = result[2] if len(result) > 2 else {}
            else:
                extracted_text = result
                quality_score = None
                meta = {}

            # LOGS DEBUG OCR (affichés dans les logs du worker)
            print("DEBUG OCR")
            print("FILE:", cv_file.storage_path, "MIME:", cv_file.mime_type)
            print("LEN TEXT:", len(extracted_text))
            print("QUALITY:", quality_score)
            print("SAMPLE:", extracted_text[:500])

        except ExtractionError as e:
            msg = str(e)
            print("### EXTRACTION ERROR:", msg)
            cv_file.status = CVFileStatus.FAILED.value
            cv_file.error_message = msg
            cv_text.status = "FAILED"
            cv_text.error_message = msg
        except Exception as e:
            # Si quelque chose casse dans l'OCR, on veut le voir clairement
            print("### EXTRACTION CRASH:", repr(e))
            msg = f"Unexpected error: {e}"
            cv_file.status = CVFileStatus.FAILED.value
            cv_file.error_message = msg
            cv_text.status = "FAILED"
            cv_text.error_message = msg
        else:
            # 5. Mise à jour en cas de succès
            cv_file.status = CVFileStatus.EXTRACTED.value
            cv_text.status = "SUCCESS"
            cv_text.extracted_text = extracted_text  # texte brut
            cv_text.quality_score = quality_score    # score qualité 0..1
            cv_text.error_message = None

        db.commit()
    finally:
        db.close()
