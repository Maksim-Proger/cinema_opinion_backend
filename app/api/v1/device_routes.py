from fastapi import APIRouter
from app.models.device_models import RegisterDeviceRequest
from app.usecases.register_device import RegisterDeviceUseCase
from app.repositories.device_repository import DeviceRepository

router = APIRouter(prefix="/devices", tags=["devices"])

@router.post("/register")
def register_device(request: RegisterDeviceRequest):
    RegisterDeviceUseCase().execute(request)
    return {"status": "ok"}

@router.post("/disable")
def disable_push(userId: str, deviceId: str):
    DeviceRepository.disable_push(userId, deviceId)
    return {"status": "push_disabled"}
