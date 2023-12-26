from pydantic import BaseModel, Field

from src.schemas.id import Id
from src.schemas.test_region import TestRegion


class TestEstablishment(BaseModel):
    id: Id = Field(..., alias="_id")
    name: str
    test_region: TestRegion


class TestEstablishmentCreate(BaseModel):
    name: str
    region_id: str
