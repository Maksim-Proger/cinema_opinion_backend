import asyncio
import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends

from project.collector.kinopoisk import KinopoiskClient
from project.gateway.api.avatar_routes import create_avatar_router
from project.gateway.api.collection_routes import create_collection_router
from project.gateway.api.device_routes import create_device_router
from project.gateway.api.event_routes import create_event_router
from project.gateway.api.security import verify_api_key
from project.gateway.scheduler.tasks import premieres_sync_worker
from project.gateway.usecases.import_premieres import ImportPremieresUseCase
from project.gateway.usecases.process_change_event import ProcessChangeEventUseCase
from project.gateway.usecases.register_device import RegisterDeviceUseCase
from project.gateway.usecases.upload_avatar import UploadAvatarUseCase
from project.notifier.rustore import RuStorePushService
from project.repository_local.avatar_repository import AvatarRepository
from project.repository_local.collection_repository import CollectionRepository
from project.repository_local.database import init_db_pool
from project.repository_local.migrations import apply_migrations
from project.repository_remote.changes_repository import ChangesRepository
from project.repository_remote.device_repository import DeviceRepository
from project.repository_remote.firebase import init_firebase
from project.repository_remote.user_repository import UserRepository
from project.utils.config import settings


# собирает приложение: создаёт объекты, связывает их между собой, подключает роуты
def create_app() -> FastAPI:
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        handlers=[logging.StreamHandler()]
    )
    logging.getLogger("httpx").setLevel(logging.WARNING)

    init_firebase()
    init_db_pool()
    os.makedirs(settings.avatars_storage_path, exist_ok=True)

    collection_repository = CollectionRepository()
    kinopoisk_client = KinopoiskClient()
    import_premieres = ImportPremieresUseCase(source=kinopoisk_client, store=collection_repository)

    avatar_repository = AvatarRepository()
    upload_avatar = UploadAvatarUseCase(store=avatar_repository)

    device_repository = DeviceRepository()
    register_device = RegisterDeviceUseCase(store=device_repository)
    process_change_event = ProcessChangeEventUseCase(
        changes=ChangesRepository(),
        members=UserRepository(),
        targets=device_repository,
        sender=RuStorePushService()
    )

    # при старте применяет миграции и запускает фоновую загрузку премьер, при остановке закрывает её
    @asynccontextmanager
    async def lifespan(backend_app: FastAPI):
        apply_migrations()
        worker = asyncio.create_task(premieres_sync_worker(import_premieres.execute))
        yield
        worker.cancel()
        kinopoisk_client.close()

    backend_app = FastAPI(
        title="RuStore Push Backend",
        version="1.0.0",
        lifespan=lifespan
    )

    backend_app.include_router(
        create_device_router(register_device=register_device, devices=device_repository),
        dependencies=[Depends(verify_api_key)],
    )
    backend_app.include_router(
        create_event_router(process_change_event=process_change_event),
        dependencies=[Depends(verify_api_key)],
    )
    backend_app.include_router(
        create_avatar_router(upload_avatar=upload_avatar, reader=avatar_repository),
        dependencies=[Depends(verify_api_key)],
    )
    backend_app.include_router(
        create_collection_router(reader=collection_repository),
        dependencies=[Depends(verify_api_key)],
    )
    return backend_app


app = create_app()  # приложение, которое запускает uvicorn (project.launcher:app)