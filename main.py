import uvicorn

from src.config import DEVELOPMENT


if __name__ == "__main__":
    uvicorn.run(
        "src.app:app",
        host="0.0.0.0",
        port=8000,
        reload=DEVELOPMENT,
        log_config="logging.json",
    )
