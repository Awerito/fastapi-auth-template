from bson import ObjectId
from fastapi import APIRouter

from src.orm.crud import CRUD
from src.orm.rabbit import send_message


sample_router = APIRouter(tags=["Sample"], prefix="/sample")
sample_collection = CRUD("sample")


@sample_router.get("/")
async def get_all_sample(skip: int = 0, limit: int = 100):
    """Get all samples"""
    return sample_collection.read_all({}, skip, limit)


@sample_router.get("/{sample_id}")
async def get_sample(sample_id: str):
    """Get sample by id"""
    return sample_collection.read({"_id": sample_id})


@sample_router.post("/")
async def create_sample(sample: dict):
    """Create sample"""
    return sample_collection.create(sample)


@sample_router.put("/{sample_id}")
async def update_sample(sample: dict, sample_id: str):
    """Update sample"""
    return sample_collection.update({"_id": sample_id}, sample)


@sample_router.delete("/{sample_id}")
async def delete_sample(sample_id: str):
    """Delete sample"""
    return sample_collection.delete({"_id": sample_id})


@sample_router.get("/send-message")
async def send_message():
    """Send message to rabbitmq"""
    send_message("hello", "Hello World!")
    return {"message": "Message sent!"}
