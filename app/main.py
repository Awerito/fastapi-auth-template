import logging

from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware


from app.auth import create_admin_user
from app.routes.auth.endpoints import routes as auth_routes
from app.config import FASTAPI_CONFIG, MIDDLEWARE_CONFIG, DEVELOPMENT


@asynccontextmanager
async def lifespan(_: FastAPI) -> None:
    # Start of the application
    if DEVELOPMENT:
        logging.warning("Running in development mode!")

    # Create the admin user if it does not exist
    user = await create_admin_user()
    if user:
        logging.warning("Admin user created!")

    yield

    # End of the application
    pass


app = FastAPI(**FASTAPI_CONFIG, lifespan=lifespan)
app.add_middleware(CORSMiddleware, **MIDDLEWARE_CONFIG)

# Endpoints
app.include_router(auth_routes)
