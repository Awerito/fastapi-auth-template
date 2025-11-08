from typing import Callable, Awaitable
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.config import DatabaseConfig
from app.utils.logger import logger


class MongoDBConnectionManager:
    def __init__(self) -> None:
        self.uri: str = DatabaseConfig.uri
        self.db_name: str = DatabaseConfig.database
        self.client: AsyncIOMotorClient | None = None
        self.db: AsyncIOMotorDatabase | None = None

    async def __aenter__(self) -> AsyncIOMotorDatabase:
        self.client = AsyncIOMotorClient(self.uri)
        self.db = self.client[self.db_name]
        return self.db

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        _ = exc_type, exc_val, exc_tb
        if self.client:
            self.client.close()


async def check_mongo_connection(
    on_ready: Callable[..., Awaitable[None]] | None = None,
) -> AsyncIOMotorDatabase:
    """
    Open a connection, ping the server, print server version, and run an
    optional post-connection hook.
    """
    client = AsyncIOMotorClient(DatabaseConfig.uri)
    db = client[DatabaseConfig.database]
    await db.command("ping")
    info = await db.client.server_info()

    logger.info(f"Connected to MongoDB server: {info.get('version', 'unknown')}")
    if on_ready is not None:
        await on_ready(db)
    return db
