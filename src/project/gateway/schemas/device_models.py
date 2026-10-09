import re

from pydantic import BaseModel, field_validator

SAFE_ID_PATTERN = re.compile(r'^[a-zA-Z0-9_\-]{1,128}$')


# тело запроса /devices/disable
class DisablePushRequest(BaseModel):
    userId: str
    deviceId: str

    # допускает в id только буквы, цифры, _ и - (до 128 знаков)
    @field_validator('userId', 'deviceId')
    @classmethod
    def validate_id(cls, v):
        if not SAFE_ID_PATTERN.match(v):
            raise ValueError("Invalid ID format")
        return v


# тело запроса /devices/register
class RegisterDeviceRequest(BaseModel):
    userId: str
    deviceId: str
    pushToken: str
    platform: str = "android"

    # допускает только платформы android и ios
    @field_validator('platform')
    @classmethod
    def validate_platform(cls, v):
        if v not in ("android", "ios"):
            raise ValueError("Invalid platform")
        return v

    # ограничивает токен 512 символами
    @field_validator('pushToken')
    @classmethod
    def validate_push_token(cls, v):
        if len(v) > 512:
            raise ValueError("pushToken too long")
        return v
