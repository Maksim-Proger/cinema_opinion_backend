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

        DeviceRepository._remove_device_from_other_users(
            current_user_key=node_user_key,
            device_id=device_id
        )

        ref = db.reference(f"list_users/{node_user_key}/devices/{device_id}")
        ref.update({
            "pushToken": push_token,
            "platform": platform,
            "pushEnabled": True,
            "lastSeenAt": int(time.time())
        })

    @staticmethod
    def _remove_device_from_other_users(current_user_key: str, device_id: str):
        users_ref = db.reference("list_users")
        snapshot = users_ref.get(shallow=True)

        if not snapshot:
            return

        for user_key in snapshot.keys():
            if user_key == current_user_key:
                continue

            device_ref = db.reference(f"list_users/{user_key}/devices/{device_id}")
            device_data = device_ref.get()

            if device_data is not None:
                device_ref.delete()

    @staticmethod
    def disable_push(node_user_key: str, device_id: str):
        ref = db.reference(f"list_users/{node_user_key}/devices/{device_id}")
        ref.update({"pushEnabled": False})
