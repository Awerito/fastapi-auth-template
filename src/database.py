import gridfs

from pymongo import MongoClient

from src.config import MONGO_URI, DATABASE_NAME


# Mongodb instance
client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]
fs = gridfs.GridFS(db)
