import logging

from pprint import pprint
from fastapi import FastAPI
from datetime import datetime
from tortoise import Tortoise
from fastapi.middleware.cors import CORSMiddleware
from tortoise.contrib.fastapi import register_tortoise

from src.config import (
    FASTAPI_CONFIG,
    MIDDLEWARE_CONFIG,
    DEVELOPMENT,
    DB_URL,
)
from src.database import TORTOISE_ORM

from src.routes.sample.sample import sample_router


app = FastAPI(**FASTAPI_CONFIG)
app.add_middleware(CORSMiddleware, **MIDDLEWARE_CONFIG)


@app.on_event("startup")
async def app_startup():
    """
    This function is called when the application starts.
    """

    if DEVELOPMENT:
        logging.warning("Running in development mode!")


@app.on_event("shutdown")
async def app_shutdown():
    logging.info("App closed!")


# Sample Endpoints
app.include_router(sample_router)
