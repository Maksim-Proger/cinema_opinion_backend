from app.services.rustore_push_service import RuStorePushService
from app.models.push_models import SendPushCommand
class SendPushUseCase:
    def execute(self, command: SendPushCommand):
        return RuStorePushService.send(
            device_push_token=command.devicePushToken,
            title=command.title,
            body=command.body
        )
