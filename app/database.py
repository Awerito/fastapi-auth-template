import motor.motor_asyncio
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.config import MONGO_URI, DATABASE_NAME


class MongoDBConnectionManager:
    def __init__(self) -> None:
        self.uri: str = MONGO_URI
        self.db_name: str = DATABASE_NAME
        self.client: AsyncIOMotorClient | None = None
        self.db: AsyncIOMotorDatabase | None = None

    async def __aenter__(self) -> AsyncIOMotorDatabase:
        self.client = motor.motor_asyncio.AsyncIOMotorClient(self.uri)
        self.db = self.client[self.db_name]
        return self.db

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        _ = exc_type, exc_val, exc_tb
        if self.client:
            self.client.close()
