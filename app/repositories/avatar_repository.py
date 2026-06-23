import os
import uuid
from app.core.config import settings
from app.core.database import get_connection, release_connection


class AvatarRepository:

    @staticmethod
    def save_avatar(user_id: str, image_bytes: bytes, content_type: str) -> str:
        avatar_id = str(uuid.uuid4())
        file_name = f"{avatar_id}.jpg"
        file_path = os.path.join(settings.avatars_storage_path, file_name)

        old_file_name = AvatarRepository._get_file_name(user_id)

        with open(file_path, "wb") as f:
            f.write(image_bytes)

        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO avatars (avatar_id, user_id, file_name, content_type, size_bytes)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (user_id) DO UPDATE SET
                        avatar_id = EXCLUDED.avatar_id,
                        file_name = EXCLUDED.file_name,
                        content_type = EXCLUDED.content_type,
                        size_bytes = EXCLUDED.size_bytes,
                        created_at = now()
                    """,
                    (avatar_id, user_id, file_name, content_type, len(image_bytes))
                )
            conn.commit()
        finally:
            release_connection(conn)

        if old_file_name and old_file_name != file_name:
            old_path = os.path.join(settings.avatars_storage_path, old_file_name)
            if os.path.exists(old_path):
                os.remove(old_path)

        return avatar_id

    @staticmethod
    def get_avatar_path(user_id: str) -> tuple[str, str] | None:
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT file_name, content_type FROM avatars WHERE user_id = %s",
                    (user_id,)
                )
                row = cur.fetchone()
        finally:
            release_connection(conn)

        if not row:
            return None

        file_name, content_type = row
        return os.path.join(settings.avatars_storage_path, file_name), content_type

    @staticmethod
    def _get_file_name(user_id: str) -> str | None:
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT file_name FROM avatars WHERE user_id = %s", (user_id,))
                row = cur.fetchone()
        finally:
            release_connection(conn)

        return row[0] if row else None
