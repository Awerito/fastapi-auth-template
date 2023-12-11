import json

from bson import json_util, ObjectId
from fastapi import HTTPException, status

from src.database import db


class CRUD:
    def __init__(self, collection, relations=[]):
        self.collection = collection
        self.db = db[collection]
        self.relations = relations

    def create(self, data):
        data["disable"] = False
        result = self.db.insert_one(data)
        return str(result.inserted_id)

    def read(self, query):
        if "_id" in query:
            if ObjectId.is_valid(query["_id"]):
                query["_id"] = ObjectId(query["_id"])

        if "disable" not in query:
            query["disable"] = False

        result = self.db.find_one(query)
        document = json.loads(json_util.dumps(result))
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Document not found"
            )

        return document

    def read_all(self, query, skip, limit):
        if "_id" in query:
            if ObjectId.is_valid(query["_id"]):
                query["_id"] = ObjectId(query["_id"])

        if "disable" not in query:
            query["disable"] = False

        results = self.db.find(query).skip(skip * limit).limit(limit)
        documents = json.loads(json_util.dumps(results))
        if not documents:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Documents not found"
            )

        return documents

    def update(self, query, data):
        if "_id" in query:
            if ObjectId.is_valid(query["_id"]):
                query["_id"] = ObjectId(query["_id"])

        results = self.db.find_one_and_update(
            query, {"$set": data}, return_document=True
        )
        if bool(results):
            for relation in self.relations:
                update_status = db[relation].update_many(
                    {self.collection: results["_id"]}, {"$set": results}
                )
                print(update_status)
        return bool(results)

    def delete(self, query):
        if "_id" in query:
            if ObjectId.is_valid(query["_id"]):
                query["_id"] = ObjectId(query["_id"])

        results = self.db.update_one(query, {"$set": {"disable": True}})
        return bool(results.modified_count)
