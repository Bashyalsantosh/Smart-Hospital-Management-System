import json
from typing import Any, Optional
import redis.asyncio as redis
from fastapi import HTTPException, status

from app.core.tenant import get_current_tenant

class TenantRedisCache:
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client

    def _get_namespaced_key(self, key: str) -> str:
        """Automatically prefixes the cache key with the current tenant ID."""
        tenant_id = get_current_tenant()
        if not tenant_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tenant context missing for cache operation."
            )
        # Sanitize key and tenant name
        safe_tenant = "".join(c for c in tenant_id if c.isalnum() or c == "_")
        return f"tenant:{safe_tenant}:{key}"

    async def get(self, key: str) -> Optional[Any]:
        """Retrieve and deserialize JSON data from Redis under the tenant namespace."""
        namespaced_key = self._get_namespaced_key(key)
        data = await self.redis.get(namespaced_key)
        if data:
            return json.loads(data)
        return None

    async def set(self, key: str, value: Any, expire_seconds: int = 300) -> None:
        """Serialize and store data in Redis under the tenant namespace with TTL."""
        namespaced_key = self._get_namespaced_key(key)
        serialized_data = json.dumps(value)
        await self.redis.set(namespaced_key, serialized_data, ex=expire_seconds)

    async def delete(self, key: str) -> None:
        """Delete a namespaced cache key."""
        namespaced_key = self._get_namespaced_key(key)
        await self.redis.delete(namespaced_key)
