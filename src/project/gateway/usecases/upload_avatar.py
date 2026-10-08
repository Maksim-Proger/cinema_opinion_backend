import io
from typing import Protocol

from PIL import Image, ImageOps, UnidentifiedImageError

from project.utils.config import settings

AVATAR_MAX_DIMENSIONS = (1600, 1600)


class AvatarStore(Protocol):
    def save_avatar(self, user_id: str, image_bytes: bytes, content_type: str) -> str: ...


class UploadAvatarUseCase:
    def __init__(self, store: AvatarStore):
        self._store = store

    def execute(self, user_id: str, raw_bytes: bytes) -> str:
        if len(raw_bytes) > settings.avatar_max_upload_bytes:
            raise ValueError("File is too large")

        try:
            image = Image.open(io.BytesIO(raw_bytes))
            image.verify()
        except (UnidentifiedImageError, OSError):
            raise ValueError("Invalid image file")

        image = Image.open(io.BytesIO(raw_bytes))
        image = ImageOps.exif_transpose(image)
        image = image.convert("RGB")
        image.thumbnail(AVATAR_MAX_DIMENSIONS, resample=Image.Resampling.LANCZOS)

        buffer = io.BytesIO()
        image.save(buffer, format="JPEG", quality=90)
        processed_bytes = buffer.getvalue()

        return self._store.save_avatar(
            user_id=user_id,
            image_bytes=processed_bytes,
            content_type="image/jpeg"
        )