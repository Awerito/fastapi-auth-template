import logging

from pprint import pprint
from fastapi import FastAPI
from datetime import datetime
from tortoise import Tortoise
from fastapi.middleware.cors import CORSMiddleware
from tortoise.contrib.fastapi import register_tortoise

from src.auth import create_admin_user
from src.routes.auth.auth import authentication_routes
from src.config import FASTAPI_CONFIG, MIDDLEWARE_CONFIG, DEVELOPMENT, DB_URL

# from src.routes.sample.sample import sample_router


app = FastAPI(**FASTAPI_CONFIG)
app.add_middleware(CORSMiddleware, **MIDDLEWARE_CONFIG)


@app.on_event("startup")
async def app_startup():
    """
    This function is called when the application starts.
    """

    if DEVELOPMENT:
        logging.warning("Running in development mode!")

    # user = await create_admin_user()
    # if user:
    #     logging.warning("Admin user created!")


@app.on_event("shutdown")
async def app_shutdown():
    logging.info("App closed!")


# Users Endpoints
app.include_router(authentication_routes)

# # Sample Endpoints
# app.include_router(sample_router)

register_tortoise(
    app,
    db_url=DB_URL,
    modules={"models": ["src.models.user"]},
    generate_schemas=True,
    add_exception_handlers=True,
)
