from fastapi import APIRouter, Depends

from src.auth import current_active_user
from src.orm.crud import CRUD
#Imports#


#SchemaNameLower#_router = APIRouter(tags=["#SchemaNameTag#"], prefix="/#SchemaNameLower#", dependencies=[Depends(current_active_user)])
#SchemaNameLower#_collection = CRUD("#SchemaNameLower#", relations=[])


@#SchemaNameLower#_router.get("/", response_model=list[#SchemaNameTag#])
async def get_all_#SchemaNameLower#(skip: int = 0, limit: int = 100):
    """Get all #SchemaNameLower#s"""
    return #SchemaNameLower#_collection.read_all({}, skip, limit)


@#SchemaNameLower#_router.get("/{#SchemaNameLower#_id}", response_model=#SchemaNameTag#)
async def get_#SchemaNameLower#(#SchemaNameLower#_id: str):
    """Get #SchemaNameLower# by id"""
    return #SchemaNameLower#_collection.read({"_id": #SchemaNameLower#_id})


@#SchemaNameLower#_router.post("/")
async def create_#SchemaNameLower#(#SchemaNameLower#: #SchemaNameTag#Create = Depends(#SchemaNameTag#Create)):
    """Create #SchemaNameLower#"""
    return #SchemaNameLower#_collection.create(#SchemaNameLower#.dict())


@#SchemaNameLower#_router.put("/{#SchemaNameLower#_id}")
async def update_#SchemaNameLower#(#SchemaNameLower#_id: str, #SchemaNameLower#: #SchemaNameTag#Create = Depends(#SchemaNameTag#Create)):
    """Update #SchemaNameLower#"""
    return #SchemaNameLower#_collection.update({"_id": #SchemaNameLower#_id}, #SchemaNameLower#.dict())


@#SchemaNameLower#_router.delete("/{#SchemaNameLower#_id}")
async def delete_#SchemaNameLower#(#SchemaNameLower#_id: str):
    """Delete #SchemaNameLower#"""
    return #SchemaNameLower#_collection.delete({"_id": #SchemaNameLower#_id})
