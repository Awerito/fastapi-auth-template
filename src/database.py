from pymongo import MongoClient
from pymongo.database import Database

from src.config import MONGO_URI, DATABASE_NAME


class MongoDBConnectionManager:
    def __init__(self):
        self.uri = MONGO_URI
        self.db_name = DATABASE_NAME
        self.client = None
        self.db = None

    def __enter__(self) -> Database:
        self.client = MongoClient(self.uri)
        self.db = self.client[self.db_name]
        return self.db

    def __exit__(self, exc_type, exc_val, exc_tb):
        _ = exc_type, exc_val, exc_tb
        if self.client:
            self.client.close()
