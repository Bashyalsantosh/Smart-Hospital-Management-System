from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
import redis.asyncio as redis
import time

from app.core.redis import get_redis_client

router = APIRouter(prefix="/health", tags=["Health"])

@router.get("/redis")
async def redis_health_check(
    redis_client: redis.Redis = Depends(get_redis_client)
):
    """
    Probes the Redis cluster via PING to verify cache layer health.
    """
    start_time = time.perf_counter()
    try:
        # Send PING command to Redis
        pong = await redis_client.ping()
        latency_ms = (time.perf_counter() - start_time) * 1000

        if pong:
            return {
                "status": "healthy",
                "service": "redis",
                "latency_ms": round(latency_ms, 2)
            }
        
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "unhealthy", "service": "redis", "detail": "No response to PING"}
        )

    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "service": "redis",
                "error": str(e)
            }
        )
