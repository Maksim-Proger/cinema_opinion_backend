from pydantic import BaseModel
class ChangeCreatedEvent(BaseModel):
    changeId: str
