import gridfs

from copy import copy
from bson import ObjectId
from urllib.parse import quote
from pymongo.database import Database
from pymongo.errors import BulkWriteError
from fastapi.responses import StreamingResponse
from fastapi import APIRouter, HTTPException, UploadFile, Security, Depends

from src.auth import current_active_user
from src.database import get_fs_instance, get_db_instance


router = APIRouter(tags=["Files"], prefix="/files")


@router.get("/")
async def get_attachments(
    page: int = 1,
    limit: int = 10,
    _: dict = Security(current_active_user, scopes=["file.all"]),
    fs: gridfs.GridFS = Depends(get_fs_instance),
):
    attachments = fs.find().skip((page - 1) * limit).limit(limit)
    return {str(attachment._id): attachment.filename for attachment in attachments}


@router.get("/{file_id}")
async def get_attachment(
    file_id: str,
    _: dict = Security(current_active_user, scopes=["file.read"]),
    db: Database = Depends(get_db_instance),
):
    fs = gridfs.GridFS(db)
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
    fs: gridfs.GridFS = Depends(get_fs_instance),
):
    try:
        file_id = fs.put(file.file, filename=file.filename)
    except BulkWriteError:
        raise HTTPException(status_code=400, detail="Invalid file")

    return {"file_id": str(file_id)}


@router.delete("/{file_id}")
async def delete_attachment(
    file_id: str,
    _: dict = Security(current_active_user, scopes=["file.delete"]),
    fs: gridfs.GridFS = Depends(get_fs_instance),
):
    attachment = fs.find_one({"_id": ObjectId(file_id)})
    if not attachment:
        raise HTTPException(status_code=404, detail="File not found")

    filename = attachment.filename
    fs.delete(ObjectId(file_id))
    return {"message": f"File {filename} deleted successfully"}