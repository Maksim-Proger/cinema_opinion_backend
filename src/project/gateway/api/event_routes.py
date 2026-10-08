from fastapi import APIRouter

from project.gateway.schemas.event_models import ChangeCreatedEvent
from project.gateway.usecases.process_change_event import ProcessChangeEventUseCase

router = APIRouter(prefix="/events", tags=["events"])


@router.post("/change-created")
def change_created(event: ChangeCreatedEvent):
    return ProcessChangeEventUseCase().execute(event)
