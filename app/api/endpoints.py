from fastapi import APIRouter, Depends
from app.dependencies.cache import get_cache_service
from app.services.cache import TenantRedisCache

router = APIRouter(prefix="/api/v1/patients", tags=["Patients"])

@router.get("/{patient_id}")
async def get_patient_details(
    patient_id: str,
    cache: TenantRedisCache = Depends(get_cache_service)
):
    cache_key = f"patient:{patient_id}"

    # 1. Check Tenant-Isolated Cache
    cached_data = await cache.get(cache_key)
    if cached_data:
        return {"source": "cache", "data": cached_data}

    # 2. Fetch from Database (Simulated)
    patient_record = {"id": patient_id, "name": "Jane Doe", "condition": "Stable"}

    # 3. Store in Tenant-Isolated Cache (Expires in 5 minutes)
    await cache.set(cache_key, patient_record, expire_seconds=300)

    return {"source": "database", "data": patient_record}
