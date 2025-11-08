import os

from pathlib import Path
from dotenv import load_dotenv
from urllib.parse import urlparse
from app.utils.logger import logger

load_dotenv()

ENV = os.getenv("ENV", "dev")
if ENV.startswith("dev"):
    logger.warning(f"Running in {ENV} mode!")


def load_api_description() -> str:
    return Path("app/docs/api_description.md").read_text(encoding="utf-8")


class FastAPIConfig:
    @classmethod
    def dict(cls):
        return {
            "title": os.getenv("API_TITLE", "FastAPI"),
            "description": load_api_description(),
            "version": os.getenv("API_VERSION", "v1.0.0"),
            "contact": {
                "name": os.getenv("API_CONTACT_NAME", "API Support"),
                "email": os.getenv("API_CONTACT_EMAIL", "example@email.com"),
            },
            "docs_url": os.getenv("API_DOCS_URL", "/docs"),
            "redoc_url": os.getenv("API_REDOC_URL", "/redoc"),
        }


class CorsConfig:
    origins = [o.strip() for o in os.getenv("CORS_ORIGINS", "").split(",") if o.strip()]
    allow_credentials = os.getenv("CORS_ALLOW_CREDENTIALS", "true").lower() == "true"
    allow_methods = [m.strip() for m in os.getenv("CORS_ALLOW_METHODS", "*").split(",")]
    allow_headers = [h.strip() for h in os.getenv("CORS_ALLOW_HEADERS", "*").split(",")]
    max_age = int(os.getenv("CORS_MAX_AGE", "600"))


class SecurityConfig:
    secret_key = os.getenv("SECRET_KEY", "supersecretkey")
    algorithm = os.getenv("ALGORITHM", "HS256")
    access_token_duration_minutes = int(
        os.getenv("ACCESS_TOKEN_DURATION_MINUTES", "30")
    )


class DatabaseConfig:
    host = os.getenv("MONGO_HOST", "localhost")
    port = int(os.getenv("MONGO_PORT", "27017"))
    username = os.getenv("MONGO_USERNAME", "user")
    password = os.getenv("MONGO_PASSWORD", "password")
    database = os.getenv("MONGO_DATABASE", "db_name")
    uri = os.getenv(
        "MONGO_URI",
        f"mongodb://{username}:{password}@{host}:{port}/{database}",
    )

    if os.getenv("MONGO_URI"):
        parsed = urlparse(uri)
        database = parsed.path.lstrip("/") or "admin"
