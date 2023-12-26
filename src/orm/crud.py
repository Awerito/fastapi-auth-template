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

        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Document not found"
            )

        document = json.loads(json_util.dumps(self._replace_foreign_keys(result)))
        return document

    def read_all(self, query, skip, limit):
        if "_id" in query:
            if ObjectId.is_valid(query["_id"]):
                query["_id"] = ObjectId(query["_id"])

        if "disable" not in query:
            query["disable"] = False

        results = self.db.find(query).skip(skip * limit).limit(limit)
        documents = [
            json.loads(json_util.dumps(self._replace_foreign_keys(result)))
            for result in results
        ]
        return documents

    def _replace_foreign_keys(self, document):
        keys_to_remove = []

        for key, value in list(document.items()):
            if key.endswith("_id") and key != "_id":
                collection_name = key[:-3]
                collection = db[collection_name]
                foreign_key_value = ObjectId(document[key])

                foreign_document = collection.find_one({"_id": foreign_key_value})
                document[collection_name] = foreign_document
                keys_to_remove.append(key)

        for key in keys_to_remove:
            del document[key]

        return document

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
        return bool(results)

    def delete(self, query):
        if "_id" in query:
            if ObjectId.is_valid(query["_id"]):
                query["_id"] = ObjectId(query["_id"])

        results = self.db.update_one(query, {"$set": {"disable": True}})
        return bool(results.modified_count)
