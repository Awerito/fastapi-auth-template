from src.config import DB_URL

TORTOISE_ORM = {
    "connections": {"default": DB_URL},
    "apps": {
        "models": {"models": ["aerich.models", "src.models.book"]},
    },
}
