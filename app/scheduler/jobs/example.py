from app.utils.logger import logger


async def example_job() -> None:
    logger.info("Example job executed")
