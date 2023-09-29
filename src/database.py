from src.config import DB_URL

TORTOISE_ORM = {
    "connections": {"default": DB_URL},
    "apps": {"models": {"models": ["users"], "default_connection": "default"}},
}
