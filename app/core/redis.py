import redis.asyncio as redis
from app.core.config import settings

# Create global Redis connection pool
redis_pool = redis.ConnectionPool.from_url(
    settings.REDIS_URL, # e.g., redis://localhost:6379/0
    decode_responses=True,
    max_connections=50
)

async def get_redis_client() -> redis.Redis:
    """Provides an async Redis client instance from the connection pool."""
    client = redis.Redis(connection_pool=redis_pool)
    try:
        yield client
    finally:
        await client.close()
