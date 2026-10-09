from fastapi import APIRouter

from project.gateway.schemas.event_models import ChangeCreatedEvent
from project.gateway.usecases.process_change_event import ProcessChangeEventUseCase


# собирает роут /events/...
def create_event_router(process_change_event: ProcessChangeEventUseCase) -> APIRouter:
    router = APIRouter(prefix="/events", tags=["events"])

    # POST /events/change-created: приложение сообщает о новой заметке, бэкенд рассылает пуши
    @router.post("/change-created")
    def change_created(event: ChangeCreatedEvent):
        return process_change_event.execute(event)

    return router