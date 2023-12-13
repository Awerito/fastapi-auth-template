from enum import Enum
from pydantic import BaseModel, Field, validator

from src.orm.crud import CRUD
from src.schemas.id import Id


class Region(BaseModel):
    id: Id = Field(..., alias="_id")
    name: str


class RegionCreate(BaseModel):
    name: str

    @validator("name")
    def name_is_not_empty(cls, v):
        if v == "":
            raise ValueError("Name is empty")
        return v


def available_region() -> list[str]:
    try:
        results = CRUD("region").read_all({}, 0, 100)
    except Exception:
        return []
    return {result["name"] for result in results}
