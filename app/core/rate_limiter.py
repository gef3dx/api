import logging
import time
from functools import wraps

from app.core.redis import get_async_redis
from app.utils.exceptions import RateLimitExceededException

logger = logging.getLogger(__name__)


class RateLimiter:
    """Rate limiting implementation using Redis."""

    def __init__(self):
        """Initialize the rate limiter."""
        self.redis_client = get_async_redis()

    async def is_allowed(self, key: str, limit: int, window: int) -> bool:
        """
        Check if an operation is allowed based on rate limits.

        Args:
            key: Redis key for this rate limit
            limit: Maximum number of operations allowed
            window: Time window in seconds

        Returns:
            bool: True if operation is allowed, False if rate limited
        """
        try:
            # Use Redis sorted set to track requests
            now = time.time()
            pipeline = self.redis_client.pipeline()

            # Remove expired entries
            pipeline.zremrangebyscore(key, 0, now - window)

            # Count current requests
            pipeline.zcard(key)

            # Add current request
            pipeline.zadd(key, {str(now): now})

            # Set expiration
            pipeline.expire(key, window)

            results = await pipeline.execute()
            current_count = results[1]

            return current_count < limit
        except Exception as e:
            logger.error(f"Error checking rate limit: {e}")
            # Fail open - allow the request if Redis is unavailable
            return True

    async def get_retry_after(self, key: str, window: int) -> int:
        """
        Get the time in seconds until the rate limit resets.

        Args:
            key: Redis key for this rate limit
            window: Time window in seconds

        Returns:
            int: Seconds until rate limit resets
        """
        try:
            now = time.time()
            earliest = await self.redis_client.zrange(key, 0, 0, withscores=True)

            if earliest:
                earliest_time = earliest[0][1]
                return max(0, int(earliest_time + window - now))

            return 0
        except Exception as e:
            logger.error(f"Error getting retry after: {e}")
            return 0


# Global rate limiter instance
rate_limiter = RateLimiter()


def rate_limit(limit: int = 10, window: int = 60, key_prefix: str = "rate_limit"):
    """
    Decorator for rate limiting endpoints.

    Args:
        limit: Maximum number of requests allowed
        window: Time window in seconds
        key_prefix: Prefix for Redis keys
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate rate limit key
            # This assumes the first argument is the request or contains user info
            key = f"{key_prefix}:{hash(str(args) + str(kwargs))}"

            # Check if allowed
            allowed = await rate_limiter.is_allowed(key, limit, window)
            if not allowed:
                retry_after = await rate_limiter.get_retry_after(key, window)
                raise RateLimitExceededException(
                    f"Rate limit exceeded. Try again in {retry_after} seconds.",
                    retry_after=retry_after,
                )

            return await func(*args, **kwargs)

        return wrapper

    return decorator
