from fastapi import APIRouter, Depends, HTTPException, Header
from app.models import ItemIn, ItemOut
from app.exceptions import ConflictError


router = APIRouter()

_fake_db = []
_next_id = 1


async def require_api_key(x_api_key: str = Header(default="")):
    if x_api_key != "secret-dev-key":
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return True


@router.get("/health", tags=["Health"])
async def health():
    return {"status": "ok"}


@router.post(
    "/items/",
    response_model=ItemOut,
    status_code=201,
    dependencies=[Depends(require_api_key)],
    tags=["Items"],
)
async def create_item(payload: ItemIn):
    global _next_id
    data = payload.model_dump()
    # Generate SKU if not provided in payload
    if not data.get("sku"):
        data["sku"] = f"AUTO-{_next_id:04d}"
    if any(it.sku == data["sku"] for it in _fake_db):
        raise ConflictError(
            message="Item with this SKU already exists", details={"sku": data["sku"]}
        )
    item = ItemOut(id=_next_id, **data)
    _fake_db.append(item)
    _next_id += 1
    return item
