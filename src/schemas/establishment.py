from pydantic import BaseModel, Field

from src.schemas.id import Id
from src.schemas.region import Region


class Establishment(BaseModel):
    id: Id = Field(..., alias="_id")
    name: str
    region: Region


class EstablishmentCreate(BaseModel):
    name: str
    region_id: str
