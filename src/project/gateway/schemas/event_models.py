import re

from pydantic import BaseModel, field_validator

SAFE_ID_PATTERN = re.compile(r'^[a-zA-Z0-9_\-]{1,128}$')


# тело запроса /events/change-created: кто создал заметку и id события
class ChangeCreatedEvent(BaseModel):
    userId: str  # Добавили поле для исключения отправителя
    changeId: str

    # допускает в id только буквы, цифры, _ и - (до 128 знаков)
    @field_validator('userId', 'changeId')
    @classmethod
    def validate_id(cls, v):
        if not SAFE_ID_PATTERN.match(v):
            raise ValueError("Invalid user ID")
        return v
