import asyncio
import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends

from project.collector.kinopoisk import KinopoiskClient
from project.gateway.api.avatar_routes import create_avatar_router
from project.gateway.api.collection_routes import create_collection_router
from project.gateway.api.device_routes import router as device_router
from project.gateway.api.event_routes import router as event_router
from project.gateway.api.security import verify_api_key
from project.gateway.scheduler.tasks import premieres_sync_worker
from project.gateway.usecases.import_premieres import ImportPremieresUseCase
from project.gateway.usecases.upload_avatar import UploadAvatarUseCase
from project.repository_local.avatar_repository import AvatarRepository
from project.repository_local.collection_repository import CollectionRepository
from project.repository_local.database import init_db_pool
from project.repository_local.migrations import apply_migrations
from project.repository_remote.firebase import init_firebase
from project.utils.config import settings


def create_app() -> FastAPI:
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        handlers=[logging.StreamHandler()]
    )

    init_firebase()
    init_db_pool()
    os.makedirs(settings.avatars_storage_path, exist_ok=True)

    collection_repository = CollectionRepository()
    kinopoisk_client = KinopoiskClient()
    import_premieres = ImportPremieresUseCase(source=kinopoisk_client, store=collection_repository)

    avatar_repository = AvatarRepository()
    upload_avatar = UploadAvatarUseCase(store=avatar_repository)

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

    backend_app.include_router(device_router, dependencies=[Depends(verify_api_key)])
    backend_app.include_router(event_router, dependencies=[Depends(verify_api_key)])
    backend_app.include_router(
        create_avatar_router(upload_avatar=upload_avatar, reader=avatar_repository),
        dependencies=[Depends(verify_api_key)],
    )
    backend_app.include_router(
        create_collection_router(reader=collection_repository),
        dependencies=[Depends(verify_api_key)],
    )
    return backend_app


app = create_app()