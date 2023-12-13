from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Query

from src.orm.crud import CRUD
from src.orm.rabbit import send_message
from src.schemas.region import available_region
from src.schemas.establishment import Establishment, EstablishmentCreate


establishment_router = APIRouter(tags=["Establishment"], prefix="/establishment")
establishment_collection = CRUD("establishment")


@establishment_router.get("/", response_model=list[Establishment])
async def get_all_establishment(skip: int = 0, limit: int = 100):
    """Get all establishments"""
    return establishment_collection.read_all({}, skip, limit)


@establishment_router.get("/{establishment_id}", response_model=Establishment)
async def get_establishment(establishment_id: str):
    """Get establishment by id"""
    return establishment_collection.read({"_id": establishment_id})


@establishment_router.post("/")
async def create_establishment(
    establishment: EstablishmentCreate = Depends(EstablishmentCreate),
    regions: list = Depends(available_region),
):
    """Create establishment"""
    if establishment.region not in regions:
        raise HTTPException(status_code=400, detail="Region does not exist")

    return establishment_collection.create(establishment.dict())


@establishment_router.put("/{establishment_id}")
async def update_establishment(
    establishment_id: str,
    establishment: EstablishmentCreate = Depends(EstablishmentCreate),
    regions: list = Depends(available_region),
):
    """Update establishment"""
    if establishment.region not in regions:
        raise HTTPException(status_code=400, detail="Region does not exist")

    return establishment_collection.update(
        {"_id": establishment_id}, establishment.dict()
    )


@establishment_router.delete("/{establishment_id}")
async def delete_establishment(establishment_id: str):
    """Delete establishment"""
    return establishment_collection.delete({"_id": establishment_id})
