import logging

from pprint import pprint
from fastapi import FastAPI
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware
from pymongo.errors import OperationFailure, ServerSelectionTimeoutError


from src.database import db
from src.auth import create_admin_user
from src.orm.rabbit import create_consumer_thread
from src.routes.auth.auth import authentication_routes
from src.config import FASTAPI_CONFIG, MIDDLEWARE_CONFIG, DEVELOPMENT

from src.routes.sample.sample import sample_router
from src.routes.establishment.establishment import establishment_router
from src.routes.region.region import region_router


app = FastAPI(**FASTAPI_CONFIG)
app.add_middleware(CORSMiddleware, **MIDDLEWARE_CONFIG)


@app.on_event("startup")
async def app_startup():
    """
    This function is called when the application starts.
    """

    if DEVELOPMENT:
        logging.warning("Running in development mode!")

    # Connect to the database
    try:
        server_info = db.client.server_info()
        logging.info(f"Connected to MongoDB server: {server_info['version']}")
    except OperationFailure as e:
        print(f"Error: {e}")
        exit(1)
    except ServerSelectionTimeoutError as e:
        print(f"Error: {e}")
        exit(1)

    # Create the admin user if it does not exist
    user = create_admin_user(db)
    if user:
        logging.warning("Admin user created!")

    # Create the consumer thread for RabbitMQ
    # create_consumer_thread()


@app.on_event("shutdown")
async def app_shutdown():
    db.client.close()


# Users Endpoints
app.include_router(authentication_routes)

# Sample Endpoints
app.include_router(sample_router)

# Endpoints
app.include_router(establishment_router)
app.include_router(region_router)
