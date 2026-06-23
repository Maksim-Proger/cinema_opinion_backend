import os
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from app.models.device_models import SAFE_ID_PATTERN
from app.repositories.avatar_repository import AvatarRepository
from app.usecases.upload_avatar import UploadAvatarUseCase

router = APIRouter(prefix="/avatars", tags=["avatars"])


@router.post("/upload")
def upload_avatar(userId: str = Form(...), file: UploadFile = File(...)):
    if not SAFE_ID_PATTERN.match(userId):
        raise HTTPException(status_code=400, detail="Invalid userId")

    raw_bytes = file.file.read()

    try:
        avatar_id = UploadAvatarUseCase().execute(user_id=userId, raw_bytes=raw_bytes)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {"status": "ok", "avatarId": avatar_id}


@router.get("/{user_id}")
def get_avatar(user_id: str):
    if not SAFE_ID_PATTERN.match(user_id):
        raise HTTPException(status_code=400, detail="Invalid userId")

    result = AvatarRepository.get_avatar_path(user_id)
    if not result:
        raise HTTPException(status_code=404, detail="Avatar not found")

    file_path, content_type = result
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Avatar not found")

    return FileResponse(file_path, media_type=content_type)
