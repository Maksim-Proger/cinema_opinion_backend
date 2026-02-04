from pydantic import BaseModel
class DevicePushTarget(BaseModel):
    userKey: str
    deviceId: str
    pushToken: str
    platform: str
