from fastapi import APIRouter, HTTPException
from app.usecases.send_push import SendPushUseCase
from app.models.push_models import SendPushCommand

router = APIRouter(
    prefix="/push",
    tags=["push"]
)

@router.post("/send")
def send_push(command: SendPushCommand):
    """
    Отправка push-уведомления на одно устройство по pushToken.
    Payload формируется на backend (RuStore).
    """
    try:
        status_code, response_text = SendPushUseCase().execute(command)
        if status_code != 200:
            raise HTTPException(
                status_code=502,
                detail={
                    "rustore_status": status_code,
                    "rustore_response": response_text
                }
            )
        return {
            "status": "sent",
            "rustore_status": status_code
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
