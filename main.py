import logging

from fastapi import FastAPI
from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator
from fastapi.middleware.cors import CORSMiddleware

from app.auth import create_admin_user
from app.api.auth import routes as auth_routes
from app.api.roles import routes as role_routes
from app.config import FASTAPI_CONFIG, MIDDLEWARE_CONFIG, DEVELOPMENT


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
    if DEVELOPMENT:
        logging.warning("Running in development mode!")

    user = await create_admin_user()
    if user:
        logging.warning("Admin user created!")

    yield


app = FastAPI(**FASTAPI_CONFIG, lifespan=lifespan)
app.add_middleware(CORSMiddleware, **MIDDLEWARE_CONFIG)
app.include_router(auth_routes)
app.include_router(role_routes)

