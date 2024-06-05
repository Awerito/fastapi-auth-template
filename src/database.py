import redis
import gridfs

from fastapi import Depends
from typing import Generator
from pymongo import MongoClient
from pymongo.database import Database

from src.config import MONGO_URI, DATABASE_NAME


def get_mongo_instance() -> Generator[Database, None, None]:
    client = MongoClient(MONGO_URI)
    try:
        yield client[DATABASE_NAME]
    finally:
        client.close()


def get_redis_instance() -> Generator[redis.Redis, None, None]:
    r = redis.Redis()
    try:
        yield r
    finally:
        r.close()


def get_fs_instance(
    db: Database = Depends(get_mongo_instance),
) -> Generator[gridfs.GridFS, None, None]:
    yield gridfs.GridFS(db)
