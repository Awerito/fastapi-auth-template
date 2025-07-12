from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorDatabase

class Role(BaseModel):
    name: str
    scopes: list[str] = []

    class Config:
        json_schema_extra = {
            "example": {"name": "admin", "scopes": ["user.me", "user.all"]}
        }

async def get_role(db: AsyncIOMotorDatabase, name: str) -> "Role | None":
    role = await db.roles.find_one({"name": name}, {"_id": 0})
    return Role(**role) if role else None
