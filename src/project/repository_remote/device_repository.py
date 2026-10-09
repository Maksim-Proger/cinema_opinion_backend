import time

from firebase_admin import db

from project.utils.models import DevicePushTarget


# устройства пользователей в Firebase
class DeviceRepository:

    # убирает устройство у других пользователей, записывает его с токеном текущему и включает пуши
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

    # выключает пуши для устройства
    @staticmethod
    def disable_push(node_user_key: str, device_id: str):
        ref = db.reference(f"list_users/{node_user_key}/devices/{device_id}")
        ref.update({"pushEnabled": False})

    # устройства с включёнными пушами у перечисленных пользователей
    @staticmethod
    def get_push_targets(node_user_keys: list[str]) -> list[DevicePushTarget]:
        targets: list[DevicePushTarget] = []

        for node_user_key in node_user_keys:
            devices_ref = db.reference(f"list_users/{node_user_key}/devices")
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
                        userKey=node_user_key,
                        deviceId=device_id,
                        pushToken=push_token,
                        platform=device_data.get("platform", "android")
                    )
                )

        return targets

    # удаляет устройство у остальных пользователей (после смены аккаунта на том же телефоне)
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