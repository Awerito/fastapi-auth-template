from pydantic import BaseModel, Field, validator

from src.schemas.id import Id
from src.schemas.region import Region


class Establishment(BaseModel):
    id: Id = Field(..., alias="_id")
    name: str
    region: str


class EstablishmentCreate(BaseModel):
    name: str
    region: str

    @validator("name")
    def name_is_not_empty(cls, v):
        if v == "":
            raise ValueError("Name is empty")
        return v
