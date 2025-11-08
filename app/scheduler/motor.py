from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.utils.logger import logger
from app.scheduler.jobs import register_jobs


scheduler = AsyncIOScheduler()


def start_scheduler() -> None:
    try:
        register_jobs(scheduler)
        scheduler.start()
        logger.info("Scheduler started successfully")
    except Exception as e:
        logger.exception("Failed to start scheduler: %s", e)


def stop_scheduler() -> None:
    try:
        scheduler.shutdown(wait=False)
        logger.info("Scheduler stopped successfully")
    except Exception as e:
        logger.exception("Failed to stop scheduler: %s", e)
