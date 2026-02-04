from app.models.device_models import RegisterDeviceRequest
from app.repositories.device_repository import DeviceRepository
class RegisterDeviceUseCase:
    """
    Use case регистрации или обновления устройства пользователя.
    """
    def execute(self, request: RegisterDeviceRequest) -> None:
        DeviceRepository.upsert_device(
            user_id=request.userId,
            device_id=request.deviceId,
            push_token=request.pushToken,
            platform=request.platform
        )
