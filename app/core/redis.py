import redis
import redis.asyncio as aioredis
from app.core.config import settings

# Synchronous Redis connection
redis_client = redis.Redis(
    host=settings.REDIS_HOST or "localhost",
    port=settings.REDIS_PORT or 6379,
    db=settings.REDIS_DB or 0,
    password=settings.REDIS_PASSWORD or None,
    decode_responses=True,
)

# Asynchronous Redis connection
async_redis_client = aioredis.Redis(
    host=settings.REDIS_HOST or "localhost",
    port=settings.REDIS_PORT or 6379,
    db=settings.REDIS_DB or 0,
    password=settings.REDIS_PASSWORD or None,
    decode_responses=True,
)


def get_redis():
    """Get synchronous Redis connection."""
    return redis_client


def get_async_redis():
    """Get asynchronous Redis connection."""
    return async_redis_client


def get_sync_redis():
    """Get a new synchronous Redis connection."""
    return redis.Redis(
        host=settings.REDIS_HOST or "localhost",
        port=settings.REDIS_PORT or 6379,
        db=settings.REDIS_DB or 0,
        password=settings.REDIS_PASSWORD or None,
        decode_responses=True,
    )