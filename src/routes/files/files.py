import gridfs

from bson import ObjectId
from urllib.parse import quote
from pymongo.database import Database
from pymongo.errors import BulkWriteError
from fastapi.responses import StreamingResponse
from fastapi import APIRouter, HTTPException, UploadFile, Security, Depends

from src.auth import current_active_user
from src.database import MongoDBConnectionManager, GridFSConnectionManager


router = APIRouter(tags=["Files"], prefix="/files")


@router.get("/")
async def get_attachments(
    page: int = 1,
    limit: int = 10,
    _: dict = Security(current_active_user, scopes=["file.all"]),
):
    with MongoDBConnectionManager() as db:
        with GridFSConnectionManager(db) as fs:
            attachments = fs.find().skip((page - 1) * limit).limit(limit)
    return {str(attachment._id): attachment.filename for attachment in attachments}


@router.get("/{file_id}")
async def get_attachment(
    file_id: str,
    _: dict = Security(current_active_user, scopes=["file.read"]),
):
    with MongoDBConnectionManager() as db:
        with GridFSConnectionManager(db) as fs:
            attachment = fs.find_one({"_id": ObjectId(file_id)})

    if not attachment:
        raise HTTPException(status_code=404, detail="File not found")

    filename = attachment.filename
    extension = filename.split(".")[-1]

    quoted_filename = quote(filename)

    return StreamingResponse(
        attachment,
        media_type=f"application/{extension}",
        headers={
            "Content-Disposition": f"attachment; filename*=UTF-8''{quoted_filename}"
        },
    )


@router.post("/")
async def upload_attachment(
    file: UploadFile,
    _: dict = Security(current_active_user, scopes=["file.write"]),
):
    try:
        with MongoDBConnectionManager() as db:
            with GridFSConnectionManager(db) as fs:
                file_id = fs.put(file.file, filename=file.filename)
    except BulkWriteError:
        raise HTTPException(status_code=400, detail="Invalid file")

    return {"file_id": str(file_id)}


@router.delete("/{file_id}")
async def delete_attachment(
    file_id: str,
    _: dict = Security(current_active_user, scopes=["file.delete"]),
):
    with MongoDBConnectionManager() as db:
        with GridFSConnectionManager(db) as fs:
            attachment = fs.find_one({"_id": ObjectId(file_id)})
            if not attachment:
                raise HTTPException(status_code=404, detail="File not found")

            filename = attachment.filename
            fs.delete(ObjectId(file_id))
    return {"message": f"File {filename} deleted successfully"}
