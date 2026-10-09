from typing import Protocol

from project.gateway.schemas.device_models import RegisterDeviceRequest


# что use case нужно от хранилища устройств
class DeviceStore(Protocol):
    # сохраняет устройство с токеном и включает на нём пуши
    def upsert_device(self, node_user_key: str, device_id: str, push_token: str, platform: str) -> None: ...


# регистрация устройства для пушей
class RegisterDeviceUseCase:
    # запоминает хранилище устройств
    def __init__(self, store: DeviceStore):
        self._store = store

    # передаёт данные из запроса в хранилище
    def execute(self, request: RegisterDeviceRequest) -> None:
        self._store.upsert_device(
            node_user_key=request.userId,
            device_id=request.deviceId,
            push_token=request.pushToken,
            platform=request.platform
        )