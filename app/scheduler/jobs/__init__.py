from apscheduler.triggers.cron import CronTrigger
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.config import ENV
from .example import example_job


def register_jobs(scheduler: AsyncIOScheduler) -> None:
    if ENV.startswith("dev"):
        scheduler.add_job(
            example_job,
            CronTrigger.from_crontab("*/5 * * * *"),
            id="example_job",
            replace_existing=True,
        )  # Every 5 minutes
    pass
