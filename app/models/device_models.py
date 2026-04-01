from pydantic import BaseModel, field_validator
import re

SAFE_ID_PATTERN = re.compile(r'^[a-zA-Z0-9_\-]{1,128}$')


class RegisterDeviceRequest(BaseModel):
    userId: str
    deviceId: str
    pushToken: str
    platform: str = "android"

    @field_validator('platform')
    @classmethod
    def validate_platform(cls, v):
        if v not in ("android", "ios"):
            raise ValueError("Invalid platform")
        return v

    @field_validator('pushToken')
    @classmethod
    def validate_push_token(cls, v):
        if len(v) > 512:
            raise ValueError("pushToken too long")
        return v
