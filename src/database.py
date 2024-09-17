import motor.motor_asyncio
from motor.motor_asyncio import AsyncIOMotorDatabase

from src.config import MONGO_URI, DATABASE_NAME


class MongoDBConnectionManager:
    def __init__(self):
        self.uri = MONGO_URI
        self.db_name = DATABASE_NAME
        self.client = None
        self.db = None

    async def __aenter__(self) -> AsyncIOMotorDatabase:
        self.client = motor.motor_asyncio.AsyncIOMotorClient(self.uri)
        self.db = self.client[self.db_name]
        return self.db

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        _ = exc_type, exc_val, exc_tb
        if self.client:
            self.client.close()
