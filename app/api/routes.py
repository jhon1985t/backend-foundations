from fastapi import APIRouter
from app.models import ItemIn, ItemOut

router = APIRouter()


@router.get("/health", tags=["Health"])
def health():
    return {"status": "ok"}


_fake_db = []
_next_id = 1


@router.post("/items/", response_model=ItemOut, status_code=201, tags=["Items"])
def create_item(payload: ItemIn):
    global _next_id
    item = ItemOut(id=_next_id, **payload.model_dump())
    _fake_db.append(item)
    _next_id += 1
    return item
