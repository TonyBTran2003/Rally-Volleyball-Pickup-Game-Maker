import time

from celery.utils.log import get_task_logger

from app.workers.celery_app import celery_app


logger = get_task_logger(__name__)


@celery_app.task(name="rally.demo_job")
def demo_job():
    logger.info("demo_job_started")

    time.sleep(5)

    logger.info("demo_job_finished")

    return {
        "message": "Rally background worker is working",
    }