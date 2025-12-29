from fastapi import APIRouter, Depends, HTTPException, Header
from app.models import ItemIn, ItemOut
from app.exceptions import ConflictError
from sqlalchemy import text
from app.db import engine


router = APIRouter()

_fake_db = []
_next_id = 1


async def require_api_key(x_api_key: str = Header(default="")):
    if x_api_key != "secret-dev-key":
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return True


@router.get("/debug/db", tags=["Debug"])
def debug_db():
    try:
        with engine.connect() as conn:
            # Try PostgreSQL query first
            try:
                db = conn.execute(text("select current_database()")).scalar()
                tables = conn.execute(
                    text(
                        """
                    select tablename
                    from pg_tables
                    where schemaname = 'public'
                    """
                    )
                ).fetchall()
                table_list = [t[0] for t in tables]
            except Exception:
                # Fallback for SQLite
                db = conn.execute(text("select 'sqlite' as db")).scalar()
                tables = conn.execute(
                    text(
                        """
                    select name
                    from sqlite_master
                    where type='table'
                    """
                    )
                ).fetchall()
                table_list = [t[0] for t in tables]

        return {
            "database": db,
            "tables": table_list,
            "engine_url": str(engine.url).replace(engine.url.password or "", "***"),
        }
    except Exception as e:
        return {
            "error": str(e),
            "database": "unavailable",
            "tables": [],
        }


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
