from fastapi import APIRouter, Depends

from src.orm.crud import CRUD
#ImportSchemas#


#SchemaName#_router = APIRouter(tags=["#SchemaNameTag#"], prefix="/#SchemaName#")
#SchemaName#_collection = CRUD("#SchemaName#", relations=[])


@#SchemaName#_router.get("/", response_model=list[#SchemaNameTag#])
async def get_all_#SchemaName#(skip: int = 0, limit: int = 100):
    """Get all #SchemaName#s"""
    return #SchemaName#_collection.read_all({}, skip, limit)


@#SchemaName#_router.get("/{#SchemaName#_id}", response_model=#SchemaNameTag#)
async def get_#SchemaName#(#SchemaName#_id: str):
    """Get #SchemaName# by id"""
    return #SchemaName#_collection.read({"_id": #SchemaName#_id})


@#SchemaName#_router.post("/")
async def create_#SchemaName#(#SchemaName#: #SchemaNameTag#Create = Depends(#SchemaNameTag#Create)):
    """Create #SchemaName#"""
    return #SchemaName#_collection.create(#SchemaName#.dict())


@#SchemaName#_router.put("/{#SchemaName#_id}")
async def update_#SchemaName#(#SchemaName#_id: str, #SchemaName#: #SchemaNameTag#Create = Depends(#SchemaNameTag#Create)):
    """Update #SchemaName#"""
    return #SchemaName#_collection.update({"_id": #SchemaName#_id}, #SchemaName#.dict())


@#SchemaName#_router.delete("/{#SchemaName#_id}")
async def delete_#SchemaName#(#SchemaName#_id: str):
    """Delete #SchemaName#"""
    return #SchemaName#_collection.delete({"_id": #SchemaName#_id})
