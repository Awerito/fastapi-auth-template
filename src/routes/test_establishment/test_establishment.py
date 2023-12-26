from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Query

from src.orm.crud import CRUD
from src.orm.rabbit import send_message
from src.schemas.test_region import available_region
from src.schemas.test_establishment import TestEstablishment, TestEstablishmentCreate


test_establishment_router = APIRouter(
    tags=["Test Establishment"], prefix="/test_establishment"
)
test_establishment_collection = CRUD("test_establishment")


@test_establishment_router.get("/", response_model=list[TestEstablishment])
async def get_all_test_establishment(skip: int = 0, limit: int = 100):
    """Get all test_establishments"""
    return test_establishment_collection.read_all({}, skip, limit)


@test_establishment_router.get(
    "/{test_establishment_id}", response_model=TestEstablishment
)
async def get_test_establishment(test_establishment_id: str):
    """Get test_establishment by id"""
    return test_establishment_collection.read({"_id": test_establishment_id})


@test_establishment_router.post("/")
async def create_test_establishment(
    test_establishment: TestEstablishmentCreate = Depends(TestEstablishmentCreate),
    regions: list = Depends(available_region),
):
    """Create test_establishment"""
    if test_establishment.region_id not in regions:
        raise HTTPException(status_code=400, detail="Region does not exist")

    return test_establishment_collection.create(test_establishment.dict())


@test_establishment_router.put("/{test_establishment_id}")
async def update_test_establishment(
    test_establishment_id: str,
    test_establishment: TestEstablishmentCreate = Depends(TestEstablishmentCreate),
    regions: list = Depends(available_region),
):
    """Update test_establishment"""
    if test_establishment.region_id not in regions:
        raise HTTPException(status_code=400, detail="Region does not exist")

    return test_establishment_collection.update(
        {"_id": test_establishment_id}, test_establishment.dict()
    )


@test_establishment_router.delete("/{test_establishment_id}")
async def delete_test_establishment(test_establishment_id: str):
    """Delete test_establishment"""
    return test_establishment_collection.delete({"_id": test_establishment_id})
