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

@celery_app.task(name="rally.process_game_joined")
def process_game_joined(game_id: int, user_id: int):
    logger.info(
        "game_joined_processed game_id=%s user_id=%s",
        game_id,
        user_id,
    )

    return {
        "event": "game_joined",
        "game_id": game_id,
        "user_id": user_id,
    }