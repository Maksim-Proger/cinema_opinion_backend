import io
from PIL import Image, UnidentifiedImageError
from app.core.config import settings
from app.repositories.avatar_repository import AvatarRepository

AVATAR_MAX_DIMENSIONS = (512, 512)


class UploadAvatarUseCase:
    """
    Валидирует, нормализует и сохраняет аватарку пользователя.
    """
    def execute(self, user_id: str, raw_bytes: bytes) -> str:
        if len(raw_bytes) > settings.avatar_max_upload_bytes:
            raise ValueError("File is too large")

        try:
            image = Image.open(io.BytesIO(raw_bytes))
            image.verify()
        except (UnidentifiedImageError, OSError):
            raise ValueError("Invalid image file")

        # verify() делает объект непригодным для дальнейшей работы — открываем заново
        image = Image.open(io.BytesIO(raw_bytes))
        image = image.convert("RGB")
        image.thumbnail(AVATAR_MAX_DIMENSIONS)

        buffer = io.BytesIO()
        image.save(buffer, format="JPEG", quality=85)
        processed_bytes = buffer.getvalue()

        return AvatarRepository.save_avatar(
            user_id=user_id,
            image_bytes=processed_bytes,
            content_type="image/jpeg"
        )
