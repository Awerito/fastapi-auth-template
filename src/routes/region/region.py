from fastapi import APIRouter, Depends

from src.orm.crud import CRUD
from src.orm.rabbit import send_message
from src.schemas.region import Region, RegionCreate


region_router = APIRouter(tags=["Region"], prefix="/region")
region_collection = CRUD("region", relations=["establishment"])


@region_router.get("/", response_model=list[Region])
async def get_all_region(skip: int = 0, limit: int = 100):
    """Get all regions"""
    return region_collection.read_all({}, skip, limit)


@region_router.get("/{region_id}", response_model=Region)
async def get_region(region_id: str):
    """Get region by id"""
    return region_collection.read({"_id": region_id})


@region_router.post("/")
async def create_region(region: RegionCreate = Depends(RegionCreate)):
    """Create region"""
    return region_collection.create(region.dict())


@region_router.put("/{region_id}")
async def update_region(region_id: str, region: RegionCreate = Depends(RegionCreate)):
    """Update region"""
    return region_collection.update({"_id": region_id}, region.dict())


@region_router.delete("/{region_id}")
async def delete_region(region_id: str):
    """Delete region"""
    return region_collection.delete({"_id": region_id})
