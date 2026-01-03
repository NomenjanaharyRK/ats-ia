"""Celery application configuration with DLQ support."""
from celery import Celery
import os

celery_app = Celery(
    "ats_worker",
    broker=os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0"),
    backend=os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/0"),
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_reject_on_worker_lost=True,
    task_default_retry_delay=60,
    task_max_retries=3,
    # Task routing
    task_routes={
        "app.workers.tasks.*": {"queue": "default"},
    },
    # Dead Letter Queue configuration
    task_annotations={
        "*": {
            "on_failure": lambda self, exc, task_id, args, kwargs, einfo: 
                celery_app.send_task(
                    "log_to_dlq",
                    args=[task_id, str(exc), args, kwargs],
                    queue="failed"
                )
        }
    },
)

# Auto-discover tasks
celery_app.autodiscover_tasks(["app.workers"])
