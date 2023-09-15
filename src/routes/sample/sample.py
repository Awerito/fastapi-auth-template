from fastapi import APIRouter, HTTPException, Depends, Security, status

from src.auth import User, current_active_user


sample_router = APIRouter()


@sample_router.get("/", tags=["Sample"])
async def sample(
    current_user: User = Security(current_active_user, scopes=["sample.read"])
):
    return {"message": "Hello World"}
