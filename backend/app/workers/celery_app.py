from celery import Celery

from app.config import (
    CELERY_BROKER_URL,
    CELERY_RESULT_BACKEND,
)


celery_app = Celery(
    "rally",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
    include=["app.workers.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    result_expires=3600,
)