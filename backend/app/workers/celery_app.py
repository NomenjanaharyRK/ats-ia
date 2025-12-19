import os
from celery import Celery


celery_app = Celery(
    "ats_tasks",
    broker=os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0"),
    backend=os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/0"),
    include=["app.workers.tasks"],
)
