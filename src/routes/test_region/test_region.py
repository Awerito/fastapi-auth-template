from fastapi import APIRouter, Depends

from src.orm.crud import CRUD
from src.orm.rabbit import send_message
from src.schemas.test_region import TestRegion, TestRegionCreate


test_region_router = APIRouter(tags=["Test Region"], prefix="/test_region")
test_region_collection = CRUD("test_region", relations=["establishment"])


@test_region_router.get("/", response_model=list[TestRegion])
async def get_all_test_region(skip: int = 0, limit: int = 100):
    """Get all test_regions"""
    return test_region_collection.read_all({}, skip, limit)


@test_region_router.get("/{test_region_id}", response_model=TestRegion)
async def get_test_region(test_region_id: str):
    """Get test_region by id"""
    return test_region_collection.read({"_id": test_region_id})


@test_region_router.post("/")
async def create_test_region(test_region: TestRegionCreate = Depends(TestRegionCreate)):
    """Create test_region"""
    return test_region_collection.create(test_region.dict())


@test_region_router.put("/{test_region_id}")
async def update_test_region(
    test_region_id: str, test_region: TestRegionCreate = Depends(TestRegionCreate)
):
    """Update test_region"""
    return test_region_collection.update({"_id": test_region_id}, test_region.dict())


@test_region_router.delete("/{test_region_id}")
async def delete_test_region(test_region_id: str):
    """Delete test_region"""
    return test_region_collection.delete({"_id": test_region_id})
