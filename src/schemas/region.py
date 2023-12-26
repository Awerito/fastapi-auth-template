from enum import Enum
from pydantic import BaseModel, Field

from src.orm.crud import CRUD
from src.schemas.id import Id


class Region(BaseModel):
    id: Id = Field(..., alias="_id")
    name: str


class RegionCreate(BaseModel):
    name: str


def available_region() -> list[str]:
    try:
        results = CRUD("region", relations=["establishment"]).read_all({}, 0, 100)
    except Exception:
        return []
    return {str(result["_id"]["$oid"]) for result in results}
