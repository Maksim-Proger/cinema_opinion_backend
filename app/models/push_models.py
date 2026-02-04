from pydantic import BaseModel
class SendPushCommand(BaseModel):
    devicePushToken: str
    title: str
    body: str
