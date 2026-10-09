from typing import Protocol

from fastapi import APIRouter, HTTPException, Path

from project.gateway.usecases.premieres import premieres_code


# что роуту нужно от хранилища: читать подборку по коду
class CollectionReader(Protocol):
    # подборка с фильмами по коду, либо None
    def get_collection_with_items(self, code: str) -> dict | None: ...


# собирает роуты /collections/...
def create_collection_router(reader: CollectionReader) -> APIRouter:
    router = APIRouter(prefix="/collections", tags=["collections"])

    # GET /collections/premieres/{year}/{month}: премьеры за месяц; нет в базе — 404
    @router.get("/premieres/{year}/{month}")
    def get_premieres(
            year: int = Path(..., ge=1995, le=2100),
            month: int = Path(..., ge=1, le=12),
    ):
        collection = reader.get_collection_with_items(premieres_code(year, month))
        if collection is None:
            raise HTTPException(status_code=404, detail="Premieres not found")

        return collection

    return router
