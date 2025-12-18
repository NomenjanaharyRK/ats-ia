from .celery_app import celery_app

@celery_app.task
def ping_task():
    return "pong"
