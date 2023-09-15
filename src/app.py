import logging

from pprint import pprint
from fastapi import FastAPI
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware


from src.auth import create_admin_user
from src.database import get_db_version, session
from src.routes.auth.auth import authentication_routes
from src.config import FASTAPI_CONFIG, MIDDLEWARE_CONFIG, DEVELOPMENT

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

    try:
        result = get_db_version()
        logging.info("Database connection established {}".format(result))
    except Exception as e:
        logging.error("Database connection could not be established: {}".format(e))
        exit(1)

    user = create_admin_user()
    if user:
        logging.warning("Admin user created!")


@app.on_event("shutdown")
async def app_shutdown():
    session.close()
    logging.info("Database connection closed.")


# Users Endpoints
app.include_router(authentication_routes)

# Sample Endpoints
app.include_router(sample_router)
