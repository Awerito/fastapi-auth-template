import logging

from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from pymongo.errors import OperationFailure, ServerSelectionTimeoutError


from src.database import db
from src.auth import create_admin_user
from src.routes.auth.auth import authentication_routes
from src.config import FASTAPI_CONFIG, MIDDLEWARE_CONFIG, DEVELOPMENT


@asynccontextmanager
async def lifespan(app: FastAPI):
    if DEVELOPMENT:
        logging.warning("Running in development mode!")

    # Connect to the database
    try:
        server_info = db.client.server_info()
        logging.info(f"Connected to MongoDB server: {server_info['version']}")
    except OperationFailure as e:
        logging.error(f"Error: {e}")
        exit(1)
    except ServerSelectionTimeoutError as e:
        logging.error(f"Error: {e}")
        exit(1)

    # Create the admin user if it does not exist
    user = create_admin_user(db)
    if user:
        logging.warning("Admin user created!")

    yield

    try:
        logging.info("Closing the database connection")
        db.client.close()
    except Exception as e:
        logging.error(f"Error: {e}")

    logging.info("Database connection closed!")


app = FastAPI(**FASTAPI_CONFIG, lifespan=lifespan)
app.add_middleware(CORSMiddleware, **MIDDLEWARE_CONFIG)

# Users Endpoints
app.include_router(authentication_routes)
