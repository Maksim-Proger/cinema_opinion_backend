import logging
from app.repositories.changes_repository import ChangesRepository
from app.repositories.user_repository import UserRepository
from app.repositories.device_query_repository import DeviceQueryRepository
from app.services.rustore_push_service import RuStorePushService
from app.models.event_models import ChangeCreatedEvent

logger = logging.getLogger(__name__)


class ProcessChangeEventUseCase:
    def execute(self, event: ChangeCreatedEvent) -> dict:
        change_id = event.changeId
        author_node_key = event.userId

        # 1. Получаем само событие из БД
        change = ChangesRepository.get_change(change_id)
        if not change:
            return {"status": "not_found"}

        # 2. Атомарно захватываем право на обработку (убрали is_processed)
        acquired = ChangesRepository.mark_as_processed(change_id)
        if not acquired:
            return {"status": "already_processed"}

        # 3. Находим ID общего списка
        shared_list_id = change.get("sharedListId")
        if not shared_list_id:
            return {"status": "invalid_event", "reason": "sharedListId missing"}

        # 4. Находим участников списка
        all_node_user_keys = UserRepository.find_users_by_shared_list(shared_list_id)

        # 5. Исключаем автора
        node_user_keys = [key for key in all_node_user_keys if key != author_node_key]

        if not node_user_keys:
            return {"status": "processed", "reason": "no_recipients_excluding_author"}

        # 6. Получаем токены устройств
        push_targets = DeviceQueryRepository.get_push_targets(node_user_keys)
        if not push_targets:
            return {"status": "processed", "reason": "no_devices"}

        # 7. Подготавливаем контент уведомления
        title = change.get("username", "Уведомление")
        body = change.get("noteText", "")

        sent = 0
        failed = 0

        # 8. Рассылка
        for target in push_targets:
            try:
                status_code, resp_text = RuStorePushService.send(
                    device_push_token=target.pushToken,
                    title=title,
                    body=body
                )
                if status_code == 200:
                    sent += 1
                else:
                    failed += 1
                    logger.warning(
                        "Push failed",
                        extra={
                            "deviceId": target.deviceId,
                            "pushToken": target.pushToken[:10] + "...",
                            "status_code": status_code,
                            "response": resp_text
                        }
                    )
            except Exception as e:
                failed += 1
                logger.error(
                    "Push exception",
                    extra={
                        "deviceId": target.deviceId,
                        "pushToken": target.pushToken[:10] + "...",
                        "error": str(e)
                    },
                    exc_info=True
                )

        return {
            "status": "processed",
            "changeId": change_id,
            "usersCount": len(node_user_keys),
            "devicesCount": len(push_targets),
            "sent": sent,
            "failed": failed
        }

