from .celery_app import celery_app

@celery_app.task
def process_cv_file(cv_file_id: int):
    # Ici on fera extraction texte + OCR + scoring.
    # Pour l’instant, simple log / TODO.
    print(f"[worker] process_cv_file {cv_file_id}")
