from typing import Protocol

from fastapi import APIRouter

from project.gateway.schemas.device_models import RegisterDeviceRequest, DisablePushRequest
from project.gateway.usecases.register_device import RegisterDeviceUseCase


class DevicePushSwitch(Protocol):
    def disable_push(self, node_user_key: str, device_id: str) -> None: ...


def create_device_router(register_device: RegisterDeviceUseCase, devices: DevicePushSwitch) -> APIRouter:
    router = APIRouter(prefix="/devices", tags=["devices"])

    @router.post("/register")
    def register(request: RegisterDeviceRequest):
        register_device.execute(request)
        return {"status": "ok"}

    @router.post("/disable")
    def disable(request: DisablePushRequest):
        devices.disable_push(request.userId, request.deviceId)
        return {"status": "push_disabled"}

    return router