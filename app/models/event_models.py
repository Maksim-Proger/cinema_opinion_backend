from pydantic import BaseModel, field_validator
import re

SAFE_ID_PATTERN = re.compile(r'^[a-zA-Z0-9_\-]{1,128}$')


class ChangeCreatedEvent(BaseModel):
    userId: str  # Добавили поле для исключения отправителя
    changeId: str

    @field_validator('userId', 'changeId')
    @classmethod
    def validate_id(cls, v):
        if not SAFE_ID_PATTERN.match(v):
            raise ValueError("Invalid user ID")
        return v
