from fastapi import APIRouter

from project.gateway.schemas.device_models import RegisterDeviceRequest, DisablePushRequest
from project.repository_remote.device_repository import DeviceRepository
from project.gateway.usecases.register_device import RegisterDeviceUseCase

router = APIRouter(prefix="/devices", tags=["devices"])


@router.post("/register")
def register_device(request: RegisterDeviceRequest):
    RegisterDeviceUseCase().execute(request)
    return {"status": "ok"}


@router.post("/disable")
def disable_push(request: DisablePushRequest):
    DeviceRepository.disable_push(request.userId, request.deviceId)
    return {"status": "push_disabled"}
