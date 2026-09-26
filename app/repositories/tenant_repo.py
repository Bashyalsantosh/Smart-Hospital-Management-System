from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.tenant import HospitalTenant
from app.schemas.tenant import HospitalTenantCreate

class TenantRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_tenant(self, tenant_in: HospitalTenantCreate) -> HospitalTenant:
        tenant = HospitalTenant(**tenant_in.model_dump())
        self.db.add(tenant)
        await self.db.flush()
        await self.db.refresh(tenant)
        return tenant

    async def get_all_tenants(self) -> list[HospitalTenant]:
        result = await self.db.execute(select(HospitalTenant))
        return list(result.scalars().all())
