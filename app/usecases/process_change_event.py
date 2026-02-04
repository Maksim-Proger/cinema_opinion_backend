import logging
from app.repositories.changes_repository import ChangesRepository
from app.repositories.user_repository import UserRepository
from app.repositories.device_query_repository import DeviceQueryRepository
from app.services.rustore_push_service import RuStorePushService
from app.models.event_model import ChangeCreatedEvent

logger = logging.getLogger(__name__)


class ProcessChangeEventUseCase:
    def execute(self, event: ChangeCreatedEvent) -> dict:
        # Извлекаем ID события и ID пользователя, который его прислал
        change_id = event.changeId
        author_id = event.userId

        # 1. Получаем само событие из БД
        change = ChangesRepository.get_change(change_id)
        if not change:
            return {"status": "not_found"}

        # 2. Проверяем, не обрабатывалось ли оно уже (защита от дублей)
        if ChangesRepository.is_processed(change):
            return {"status": "already_processed"}

        shared_list_id = change.get("sharedListId")
        if not shared_list_id:
            return {"status": "invalid_event", "reason": "sharedListId missing"}

        # 3. Находим ВСЕХ участников общего списка
        all_user_keys = UserRepository.find_users_by_shared_list(shared_list_id)

        # 4. ФИЛЬТРАЦИЯ: Оставляем только тех, кто НЕ является автором (userId из запроса)
        user_keys = [uid for uid in all_user_keys if uid != author_id]

        if not user_keys:
            # Если после исключения автора рассылать некому
            ChangesRepository.mark_as_processed(change_id)
            return {"status": "processed", "reason": "no_recipients_excluding_author"}

        # 5. Получаем токены устройств только для отфильтрованных пользователей
        push_targets = DeviceQueryRepository.get_push_targets(user_keys)
        if not push_targets:
            ChangesRepository.mark_as_processed(change_id)
            return {"status": "processed", "reason": "no_devices"}

        # 6. Подготавливаем контент уведомления
        title = change.get("username", "Уведомление")
        body = change.get("noteText", "")

        sent = 0
        failed = 0

        # 7. Рассылка по найденным устройствам
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

        # 8. Финализация: помечаем изменение как обработанное
        ChangesRepository.mark_as_processed(change_id)

        return {
            "status": "processed",
            "changeId": change_id,
            "usersCount": len(user_keys),  # Количество людей, получивших пуш
            "devicesCount": len(push_targets),  # Общее количество их девайсов
            "sent": sent,
            "failed": failed
        }

# import logging
# from app.repositories.changes_repository import ChangesRepository
# from app.repositories.user_repository import UserRepository
# from app.repositories.device_query_repository import DeviceQueryRepository
# from app.services.rustore_push_service import RuStorePushService
#
# logger = logging.getLogger(__name__)
#
# class ProcessChangeEventUseCase:
#     def execute(self, change_id: str) -> dict:
#         change = ChangesRepository.get_change(change_id)
#         if not change:
#             return {"status": "not_found"}
#
#         if ChangesRepository.is_processed(change):
#             return {"status": "already_processed"}
#
#         shared_list_id = change.get("sharedListId")
#         if not shared_list_id:
#             return {"status": "invalid_event", "reason": "sharedListId missing"}
#
#         user_keys = UserRepository.find_users_by_shared_list(shared_list_id)
#         if not user_keys:
#             ChangesRepository.mark_as_processed(change_id)
#             return {"status": "processed", "reason": "no_recipients"}
#
#         push_targets = DeviceQueryRepository.get_push_targets(user_keys)
#         if not push_targets:
#             ChangesRepository.mark_as_processed(change_id)
#             return {"status": "processed", "reason": "no_devices"}
#
#         title = change.get("username", "Уведомление")
#         body = change.get("noteText", "")
#
#         sent = 0
#         failed = 0
#         for target in push_targets:
#             try:
#                 status_code, resp_text = RuStorePushService.send(
#                     device_push_token=target.pushToken,
#                     title=title,
#                     body=body
#                 )
#                 if status_code == 200:
#                     sent += 1
#                 else:
#                     failed += 1
#                     logger.warning(
#                         "Push failed",
#                         extra={
#                             "deviceId": target.deviceId,
#                             "pushToken": target.pushToken[:10] + "...",
#                             "status_code": status_code,
#                             "response": resp_text
#                         }
#                     )
#             except Exception as e:
#                 failed += 1
#                 logger.error(
#                     "Push exception",
#                     extra={
#                         "deviceId": target.deviceId,
#                         "pushToken": target.pushToken[:10] + "...",
#                         "error": str(e)
#                     },
#                     exc_info=True
#                 )
#
#         ChangesRepository.mark_as_processed(change_id)
#
#         return {
#             "status": "processed",
#             "changeId": change_id,
#             "usersCount": len(user_keys),
#             "devicesCount": len(push_targets),
#             "sent": sent,
#             "failed": failed
#         }