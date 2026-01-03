"""Celery tasks with idempotence, retries, and structured logging."""
import logging
import structlog
from celery import shared_task
from celery.exceptions import MaxRetriesExceededError
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.db.session import SessionLocal
from app.models.cv_file import CVFile, CVFileStatus
from app.models.cv_text import CVText
from app.services.cv_extraction import extract_cv_text, ExtractionError
from app.models.parsed_cv import ParsedCV
from app.models.offer import Offer
from app.models.application import Application
from app.services.cv_parser import CVParser
from app.services.cv_scorer import CVScorer

# Configure structured logging
logger = structlog.get_logger(__name__)


@shared_task(name="app.workers.tasks.process_cv_file",
    bind=True,
    autoretry_for=(OSError, ConnectionError),
    max_retries=3,
    retry_backoff=True,
    retry_backoff_max=600,
    retry_jitter=True
)
def process_cv_file(self, cv_file_id: int) -> None:
    """
    Tâche Celery qui :
    - récupère un CVFile et son CVText associé,
    - lance l'extraction de texte,
    - met à jour les statuts et stocke le texte + quality_score.
    
    Idempotent: safe to retry without side effects.
    """
    task_id = self.request.id
    log = logger.bind(task_id=task_id, cv_file_id=cv_file_id)
    
    log.info("process_cv_file_start")

    db: Session = SessionLocal()
    try:
        # 1. Charger le fichier CV
        cv_file: CVFile | None = db.get(CVFile, cv_file_id)
        if not cv_file:
            log.error("cv_file_not_found")
            return
        
        log = log.bind(
            application_id=cv_file.application_id,
            original_filename=cv_file.original_filename,
            current_status=cv_file.status
        )

        # 2. IDEMPOTENCE CHECK: Don't reprocess if already done or in progress
        if cv_file.status in [CVFileStatus.EXTRACTED.value, CVFileStatus.EXTRACTING.value]:
            log.info(
                "task_already_processed_or_in_progress",
                status=cv_file.status
            )
            return
        
        # If status is FAILED, we allow retry (manual or automatic)
        
        # 3. Marquer le fichier comme en cours d'extraction (atomic state transition)
        cv_file.status = CVFileStatus.EXTRACTING.value
        db.flush()
        db.commit()  # Commit state change immediately
        
        log.info("extraction_started")

        # 4. Récupérer la ligne CVText associée à la candidature
        cv_text: CVText | None = (
            db.query(CVText)
            .filter(CVText.application_id == cv_file.application_id)
            .one_or_none()
        )
        if not cv_text:
            error_msg = "No CVText row for this application"
            log.error("cv_text_not_found")
            cv_file.status = CVFileStatus.FAILED.value
            cv_file.error_message = error_msg
            db.commit()
            return

        # 5. Extraction de texte + debug OCR
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

            log.info(
                "extraction_successful",
                text_length=len(extracted_text),
                quality_score=quality_score,
                meta=meta
            )

        except ExtractionError as e:
            msg = str(e)
            log.error("extraction_error", error=msg, error_type="ExtractionError")
            
            cv_file.status = CVFileStatus.FAILED.value
            cv_file.error_message = msg
            cv_text.status = "FAILED"
            cv_text.error_message = msg
            db.commit()
            
            # Don't retry ExtractionError (permanent failure)
            return
            
        except Exception as e:
            # Unexpected error - will be retried if transient
            log.error(
                "extraction_unexpected_error",
                error=repr(e),
                error_type=type(e).__name__
            )
            
            # Mark as extracting (not failed) to allow retry
            cv_file.error_message = f"Retry {self.request.retries + 1}/{self.max_retries}: {e}"
            db.commit()
            
            # Raise to trigger retry
            raise
        
        # 6. Mise à jour en cas de succès
        cv_file.status = CVFileStatus.EXTRACTED.value
        cv_file.error_message = None
        cv_text.status = "SUCCESS"
        cv_text.extracted_text = extracted_text
        cv_text.quality_score = quality_score
        cv_text.error_message = None

        db.commit()
        log.info("process_cv_file_success")
        
    except MaxRetriesExceededError:
        log.error("max_retries_exceeded")
        # Move to DLQ-like state
        try:
            cv_file.status = CVFileStatus.FAILED.value
            cv_file.error_message = "Max retries exceeded"
            if cv_text:
                cv_text.status = "FAILED"
                cv_text.error_message = "Max retries exceeded"
            db.commit()
        except Exception as commit_error:
            log.error("failed_to_update_status_after_max_retries", error=repr(commit_error))
        raise
        
    except Exception as e:
        log.error("process_cv_file_error", error=repr(e), error_type=type(e).__name__)
        db.rollback()
        raise
        
    finally:
        db.close()
        log.info("process_cv_file_end")
