import os
from typing import Protocol

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse

from project.gateway.schemas.device_models import SAFE_ID_PATTERN
from project.gateway.usecases.upload_avatar import UploadAvatarUseCase

# что роуту нужно от хранилища: найти файл аватарки
class AvatarReader(Protocol):
    # путь к файлу аватарки и его тип, либо None
    def get_avatar_path(self, user_id: str) -> tuple[str, str] | None: ...


# собирает роуты /avatars/...
def create_avatar_router(upload_avatar: UploadAvatarUseCase, reader: AvatarReader) -> APIRouter:
    router = APIRouter(prefix="/avatars", tags=["avatars"])

    # POST /avatars/upload: загрузить аватарку; неверный id или файл — 400
    @router.post("/upload")
    def upload(userId: str = Form(...), file: UploadFile = File(...)):
        if not SAFE_ID_PATTERN.match(userId):
            raise HTTPException(status_code=400, detail="Invalid userId")

        raw_bytes = file.file.read()

        try:
            avatar_id = upload_avatar.execute(user_id=userId, raw_bytes=raw_bytes)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

        return {"status": "ok", "avatarId": avatar_id}

    # GET /avatars/{user_id}: отдать аватарку файлом; нет — 404
    @router.get("/{user_id}")
    def get_avatar(user_id: str):
        if not SAFE_ID_PATTERN.match(user_id):
            raise HTTPException(status_code=400, detail="Invalid userId")

        result = reader.get_avatar_path(user_id)
        if not result:
            raise HTTPException(status_code=404, detail="Avatar not found")

        file_path, content_type = result
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Avatar not found")

        return FileResponse(file_path, media_type=content_type)

    return router
