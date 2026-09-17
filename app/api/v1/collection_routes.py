from fastapi import APIRouter, HTTPException, Path
from app.core.kinopoisk import premieres_code
from app.repositories.collection_repository import CollectionRepository

router = APIRouter(prefix="/collections", tags=["collections"])


@router.get("/premieres/{year}/{month}")
def get_premieres(
    year: int = Path(..., ge=1995, le=2100),
    month: int = Path(..., ge=1, le=12),
):
    collection = CollectionRepository.get_collection_with_items(
        premieres_code(year, month - 1)
    )
    if collection is None:
        raise HTTPException(status_code=404, detail="Premieres not found")

    return collection
