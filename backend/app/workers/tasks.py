from celery import shared_task
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.cv_file import CVFile, CVFileStatus
from app.models.cv_text import CVText
from app.services.cv_extraction import extract_cv_text, ExtractionError


@shared_task(name="app.workers.tasks.process_cv_file")
def process_cv_file(cv_file_id: int) -> None:
    db: Session = SessionLocal()
    try:
        cv_file: CVFile | None = db.get(CVFile, cv_file_id)
        if not cv_file:
            return

        cv_file.status = CVFileStatus.EXTRACTING.value
        db.flush()

        cv_text: CVText | None = (
            db.query(CVText)
            .filter(CVText.application_id == cv_file.application_id)
            .one_or_none()
        )
        if not cv_text:
            cv_file.status = CVFileStatus.FAILED.value
            cv_file.error_message = "No CVText row for this application"
            db.commit()
            return

        try:
            extracted = extract_cv_text(cv_file.storage_path, cv_file.mime_type)
        except ExtractionError as e:
            msg = str(e)
            cv_file.status = CVFileStatus.FAILED.value
            cv_file.error_message = msg
            cv_text.status = "FAILED"
            cv_text.error_message = msg
        except Exception as e:
            msg = f"Unexpected error: {e}"
            cv_file.status = CVFileStatus.FAILED.value
            cv_file.error_message = msg
            cv_text.status = "FAILED"
            cv_text.error_message = msg
        else:
            cv_file.status = CVFileStatus.EXTRACTED.value
            cv_text.status = "SUCCESS"
            cv_text.extracted_text = extracted
            cv_text.error_message = None

        db.commit()
    finally:
        db.close()
