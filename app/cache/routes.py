from fastapi import APIRouter

from app.cache import get_redis


router = APIRouter(prefix="/cache", tags=["Cache"])


@router.get("/ping")
async def cache_ping():
    redis = await get_redis()
    pong = await redis.ping()
    return {"redis": pong}
