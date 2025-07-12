from fastapi import APIRouter, HTTPException, Depends, Security, status

from app.database import MongoDBConnectionManager
from app.auth import User, current_active_user
from app.roles import Role, get_role

routes = APIRouter(prefix="/role", tags=["Roles"])


@routes.post("/", response_model=Role)
async def create_role(role: Role, _: User = Security(current_active_user, scopes=["admin"])) -> Role:
    async with MongoDBConnectionManager() as db:
        existing = await get_role(db, role.name)
        if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Role already exists")
        await db.roles.insert_one(role.model_dump())
    return role


@routes.get("/{name}/", response_model=Role)
async def read_role(name: str, _: User = Security(current_active_user, scopes=["admin"])) -> Role:
    async with MongoDBConnectionManager() as db:
        role = await get_role(db, name)
        if not role:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
        return role


@routes.put("/{name}/", response_model=Role)
async def update_role(name: str, role: Role, _: User = Security(current_active_user, scopes=["admin"])) -> Role:
    async with MongoDBConnectionManager() as db:
        _role = await get_role(db, name)
        if not _role:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
        await db.roles.update_one({"name": name}, {"$set": role.model_dump()})
    return role


@routes.delete("/{name}/")
async def delete_role(name: str, _: User = Security(current_active_user, scopes=["admin"])) -> None:
    async with MongoDBConnectionManager() as db:
        result = await db.roles.delete_one({"name": name})
        if result.deleted_count == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    raise HTTPException(status_code=status.HTTP_200_OK, detail="Role deleted")


@routes.get("/", response_model=list[Role])
async def list_roles(_: User = Security(current_active_user, scopes=["admin"])) -> list[Role]:
    async with MongoDBConnectionManager() as db:
        roles = await db.roles.find({}, {"_id": 0}).to_list(None)
    return [Role(**r) for r in roles]
