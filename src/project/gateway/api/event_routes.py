from fastapi import APIRouter

from project.gateway.schemas.event_models import ChangeCreatedEvent
from project.gateway.usecases.process_change_event import ProcessChangeEventUseCase


def create_event_router(process_change_event: ProcessChangeEventUseCase) -> APIRouter:
    router = APIRouter(prefix="/events", tags=["events"])

    @router.post("/change-created")
    def change_created(event: ChangeCreatedEvent):
        return process_change_event.execute(event)

    return router