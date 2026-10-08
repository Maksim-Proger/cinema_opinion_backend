from typing import Protocol

from project.gateway.schemas.device_models import RegisterDeviceRequest


class DeviceStore(Protocol):
    def upsert_device(self, node_user_key: str, device_id: str, push_token: str, platform: str) -> None: ...


class RegisterDeviceUseCase:
    def __init__(self, store: DeviceStore):
        self._store = store

    def execute(self, request: RegisterDeviceRequest) -> None:
        self._store.upsert_device(
            node_user_key=request.userId,
            device_id=request.deviceId,
            push_token=request.pushToken,
            platform=request.platform
        )