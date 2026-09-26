from fastapi import Depends
import redis.asyncio as redis
from app.core.redis import get_redis_client
from app.services.cache import TenantRedisCache

def get_cache_service(
    redis_client: redis.Redis = Depends(get_redis_client)
) -> TenantRedisCache:
    """FastAPI dependency yielding a tenant-isolated cache service."""
    return TenantRedisCache(redis_client=redis_client)
