from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader

from project.utils.config import settings

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)  # откуда брать ключ: заголовок X-API-Key (ошибку при его отсутствии выдаём сами)


# пропускает запрос только с верным ключом в заголовке X-API-Key, иначе ответ 403
def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != settings.api_secret_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or missing API Key"
        )
