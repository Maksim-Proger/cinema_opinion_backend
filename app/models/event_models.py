from pydantic import BaseModel
class ChangeCreatedEvent(BaseModel):
    userId: str # Добавили поле для исключения отправителя
    changeId: str
