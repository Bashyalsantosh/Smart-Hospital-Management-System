from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.tenant import HospitalTenantCreate, HospitalTenantResponse
from app.repositories.tenant_repo import TenantRepository
from app.api.deps import RoleChecker
from app.models.user import UserRole, User

router = APIRouter()

super_admin_role = RoleChecker([UserRole.SUPER_ADMIN])

@router.post("/", response_model=HospitalTenantResponse, status_code=status.HTTP_201_CREATED)
async def register_hospital_tenant(
    tenant_in: HospitalTenantCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(super_admin_role)
):
    repo = TenantRepository(db)
    tenant = await repo.create_tenant(tenant_in)
    return HospitalTenantResponse.model_validate(tenant)

@router.get("/", response_model=list[HospitalTenantResponse])
async def list_hospital_tenants(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(super_admin_role)
):
    repo = TenantRepository(db)
    tenants = await repo.get_all_tenants()
    return [HospitalTenantResponse.model_validate(t) for t in tenants]
