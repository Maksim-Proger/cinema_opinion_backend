import logging
import os
from fastapi import FastAPI, Depends
from app.core.security import verify_api_key
from app.core.firebase import init_firebase
from app.core.database import init_db_pool
from app.core.config import settings
from app.api.v1.device_routes import router as device_router
from app.api.v1.event_routes import router as event_router
from app.api.v1.avatar_routes import router as avatar_router

def create_app() -> FastAPI:
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        handlers=[logging.StreamHandler()]
    )

    backend_app = FastAPI(
        title="RuStore Push Backend",
        version="1.0.0"
    )
    init_firebase()
    init_db_pool()
    os.makedirs(settings.avatars_storage_path, exist_ok=True)


    backend_app.include_router(device_router, dependencies=[Depends(verify_api_key)])
    backend_app.include_router(event_router, dependencies=[Depends(verify_api_key)])
    backend_app.include_router(avatar_router, dependencies=[Depends(verify_api_key)])
    return backend_app

app = create_app()

