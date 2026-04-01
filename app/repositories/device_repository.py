import time
from firebase_admin import db


class DeviceRepository:

    @staticmethod
    def upsert_device(
            node_user_key: str,
            device_id: str,
            push_token: str,
            platform: str
    ):
        ref = db.reference(f"list_users/{node_user_key}/devices/{device_id}")
        ref.update({
            "pushToken": push_token,
            "platform": platform,
            "pushEnabled": True,
            "lastSeenAt": int(time.time())
        })

    @staticmethod
    def disable_push(node_user_key: str, device_id: str):
        ref = db.reference(f"list_users/{node_user_key}/devices/{device_id}")
        ref.update({"pushEnabled": False})
