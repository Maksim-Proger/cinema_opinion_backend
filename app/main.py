import logging
from fastapi import FastAPI
from app.core.firebase import init_firebase
from app.api.v1.device_routes import router as device_router
from app.api.v1.push_routes import router as push_router
from app.api.v1.event_routes import router as event_router

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
    backend_app.include_router(device_router)
    backend_app.include_router(push_router)
    backend_app.include_router(event_router)
    return backend_app

app = create_app()

