from firebase_admin import db
from app.models.device_push_models import DevicePushTarget
class DeviceQueryRepository:
    """
    Чтение устройств пользователей для fan-out push.
    """
    @staticmethod
    def get_push_targets(user_keys: list[str]) -> list[DevicePushTarget]:
        targets: list[DevicePushTarget] = []
        for user_key in user_keys:
            devices_ref = db.reference(f"users/{user_key}/devices")
            devices_snapshot = devices_ref.get()
            if not devices_snapshot:
                continue
            for device_id, device_data in devices_snapshot.items():
                if not device_data:
                    continue
                if not device_data.get("pushEnabled", False):
                    continue
                push_token = device_data.get("pushToken")
                if not push_token:
                    continue
                targets.append(
                    DevicePushTarget(
                        userKey=user_key,
                        deviceId=device_id,
                        pushToken=push_token,
                        platform=device_data.get("platform", "android")
                    )
                )
        return targets
