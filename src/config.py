from os import getenv
from dotenv import load_dotenv


# Load env vars
load_dotenv()

# Fastapi config
API_VERSION = getenv("API_VERSION", "0.1.0")
API_TITLE = getenv("API_TITLE", "FastAPI")
API_DESCRIPTION = getenv(
    "API_DESCRIPTION", "FastAPI is a Python framework for building blazing fast APIs."
)
API_OPENAPI_URL = getenv("API_OPENAPI_URL", "/openapi.json")

ALLOWED_ORIGINS = getenv("ALLOWED_ORIGINS", "*").split(",")
ALLOWED_METHODS = getenv("ALLOWED_METHODS", "*").split(",")
ALLOWED_HEADERS = getenv("ALLOWED_HEADERS", "*").split(",")

FASTAPI_CONFIG = {
    "title": API_TITLE,
    "description": API_DESCRIPTION,
    "openapi_url": API_OPENAPI_URL,
    "swagger_ui_parameters": {"defaultModelsExpandDepth": -1},
}

MIDDLEWARE_CONFIG = {
    "allow_origins": ALLOWED_ORIGINS,
    "allow_credentials": True,
    "allow_methods": ["*"],
    "allow_headers": ["*"],
}

# Enviroment variables
DEVELOPMENT = getenv("DEVELOPMENT", "true").lower() == "true"

MONGO_USER = getenv("MONGO_USER", "admin")
MONGO_PASS = getenv("MONGO_PASS", "admin")
MONGO_HOST = getenv("MONGO_HOST", "localhost")
MONGO_URI = f"mongodb://{MONGO_USER}:{MONGO_PASS}@{MONGO_HOST}/admin"
DATABASE_NAME = getenv("DATABASE_NAME", "fastapi")
