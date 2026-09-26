import pytest
from unittest.mock import patch
from fakeredis.aioredis import FakeAsyncRedis
from fastapi import HTTPException
import redis.exceptions

from app.services.cache import TenantRedisCache


@pytest.fixture
def fake_redis():
    """Provides an in-memory asynchronous FakeRedis instance with TTL support."""
    return FakeAsyncRedis(decode_responses=True)


@pytest.fixture
def cache_service(fake_redis):
    return TenantRedisCache(redis_client=fake_redis)


@pytest.mark.asyncio
@patch("app.services.cache.get_current_tenant")
async def test_cache_ttl_expiration(mock_get_tenant, cache_service, fake_redis):
    """Verify that cached items respect TTL and expire correctly."""
    mock_get_tenant.return_value = "hospital_alpha"

    # Set cache with a 1-second expiration
    await cache_service.set("temp:token", "expired-data", expire_seconds=1)

    # Verify key exists initially
    assert await fake_redis.exists("tenant:hospital_alpha:temp:token") == 1

    # Simulate TTL expiration in fakeredis
    await fake_redis.expire("tenant:hospital_alpha:temp:token", 0)

    # Verify key is gone
    result = await cache_service.get("temp:token")
    assert result is None


@pytest.mark.asyncio
@patch("app.services.cache.get_current_tenant")
async def test_tenant_id_sanitization_in_cache_keys(mock_get_tenant, cache_service, fake_redis):
    """Verify that tenant IDs containing special characters are safely sanitized."""
    # Malicious or unusual tenant ID input
    mock_get_tenant.return_value = "hospital;alpha--drop"

    await cache_service.set("status", "active")

    # Only alphanumeric characters and underscores should remain in the namespace
    expected_key = "tenant:hospitalalphadrop:status"
    assert await fake_redis.exists(expected_key) == 1
    assert await cache_service.get("status") == "active"


@pytest.mark.asyncio
@patch("app.services.cache.get_current_tenant")
async def test_redis_connection_error_handling(mock_get_tenant, cache_service, fake_redis):
    """Verify that Redis connection errors propagate cleanly as HTTP exceptions or custom errors."""
    mock_get_tenant.return_value = "hospital_alpha"

    # Force Redis get method to raise a connection error
    async def mock_get(*args, **kwargs):
        raise redis.exceptions.ConnectionError("Redis connection lost")

    fake_redis.get = mock_get

    with pytest.raises(redis.exceptions.ConnectionError):
        await cache_service.get("patient:1001")
