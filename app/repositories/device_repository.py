import time
from firebase_admin import db
class DeviceRepository:
    @staticmethod
    def upsert_device(
        user_id: str,
        device_id: str,
        push_token: str,
        platform: str
    ):
        ref = db.reference(f"users/{user_id}/devices/{device_id}")
        ref.update({
            "pushToken": push_token,
            "platform": platform,
            "pushEnabled": True,
            "lastSeenAt": int(time.time())
        })
    @staticmethod
    def disable_push(user_id: str, device_id: str):
        ref = db.reference(f"users/{user_id}/devices/{device_id}")
        ref.update({"pushEnabled": False})
