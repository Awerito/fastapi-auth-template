from fastapi import APIRouter
from app.config import ENV, FastAPIConfig

router = APIRouter(tags=["Healthcheck"])


@router.get("/", summary="Healthcheck")
def healthcheck():
    info = FastAPIConfig.dict()
    response = {
        "status": "ok",
        "name": info.get("title"),
        "version": info.get("version"),
        "env": ENV,
    }
    if ENV.startswith("dev"):
        response["docs_url"] = info.get("docs_url")

    return response
