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
        # Ищем этот deviceId у других пользователей и удаляем
        DeviceRepository._remove_device_from_other_users(
            current_user_key=node_user_key,
            device_id=device_id
        )

        # Сохраняем/обновляем запись у текущего пользователя
        ref = db.reference(f"list_users/{node_user_key}/devices/{device_id}")
        ref.update({
            "pushToken": push_token,
            "platform": platform,
            "pushEnabled": True,
            "lastSeenAt": int(time.time())
        })

    @staticmethod
    def _remove_device_from_other_users(current_user_key: str, device_id: str):
        """
        Находит deviceId у других пользователей и удаляет его.
        Нужно при смене аккаунта на том же устройстве.
        """
        users_ref = db.reference("list_users")
        # Ищем только узлы где есть нужный deviceId
        # Firebase не поддерживает вложенный поиск, читаем всех
        snapshot = users_ref.get(shallow=True)  # только ключи пользователей

        if not snapshot:
            return

        for user_key in snapshot.keys():
            if user_key == current_user_key:
                continue  # текущего пропускаем

            device_ref = db.reference(f"list_users/{user_key}/devices/{device_id}")
            device_data = device_ref.get()

            if device_data is not None:
                device_ref.delete()

    @staticmethod
    def disable_push(node_user_key: str, device_id: str):
        ref = db.reference(f"list_users/{node_user_key}/devices/{device_id}")
        ref.update({"pushEnabled": False})
