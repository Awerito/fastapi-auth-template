from fastapi import APIRouter, HTTPException, Depends, Security, status


sample_router = APIRouter()


@sample_router.get("/", tags=["Sample"])
async def sample():
    return {"message": "Hello World"}
