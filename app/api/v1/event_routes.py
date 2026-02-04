from fastapi import APIRouter
from app.models.event_models import ChangeCreatedEvent
from app.usecases.process_change_event import ProcessChangeEventUseCase

router = APIRouter(prefix="/events", tags=["events"])

@router.post("/change-created")
def change_created(event: ChangeCreatedEvent):
    return ProcessChangeEventUseCase().execute(event)
