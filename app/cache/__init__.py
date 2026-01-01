from redis.asyncio import Redis

from app.settings import settings


redis_client: Redis | None = None


async def get_redis() -> Redis:
    global redis_client
    if redis_client is None:
        # Connect using env-driven Redis URL (REDIS_URL); falls back to settings default
        redis_client = Redis.from_url(settings.redis_url, decode_responses=True)
    return redis_client
