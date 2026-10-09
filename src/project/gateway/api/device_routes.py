from typing import Protocol

from fastapi import APIRouter

from project.gateway.schemas.device_models import RegisterDeviceRequest, DisablePushRequest
from project.gateway.usecases.register_device import RegisterDeviceUseCase


# что роуту нужно от хранилища: выключать пуши устройству
class DevicePushSwitch(Protocol):
    # выключает пуши для устройства пользователя
    def disable_push(self, node_user_key: str, device_id: str) -> None: ...


# собирает роуты /devices/...
def create_device_router(register_device: RegisterDeviceUseCase, devices: DevicePushSwitch) -> APIRouter:
    router = APIRouter(prefix="/devices", tags=["devices"])

    # POST /devices/register: запомнить устройство и его токен для пушей
    @router.post("/register")
    def register(request: RegisterDeviceRequest):
        register_device.execute(request)
        return {"status": "ok"}

    # POST /devices/disable: выключить пуши на устройстве (при выходе из аккаунта)
    @router.post("/disable")
    def disable(request: DisablePushRequest):
        devices.disable_push(request.userId, request.deviceId)
        return {"status": "push_disabled"}

    return router