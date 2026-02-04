from pydantic import BaseModel
class RegisterDeviceRequest(BaseModel):
    userId: str
    deviceId: str
    pushToken: str
    platform: str = "android"
