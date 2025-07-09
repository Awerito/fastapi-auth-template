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
    "version": API_VERSION,
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

# MongoDB config
MONGO_URI = getenv("MONGO_URI", "mongodb://localhost:27017")
DATABASE_NAME = getenv("DATABASE_NAME", "fastapi")

# JWT config
SECRET_KEY = getenv("SECRET_KEY", "")
ALGORITHM = getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_DURATION_MINUTES = int(getenv("ACCESS_TOKEN_DURATION_MINUTES", 60))
