from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.reports import OperationalMetricsSummary, FinancialSummary, FEFOExpiryAlertSummary
from app.services.reports_service import ReportsService
from app.api.deps import RoleChecker
from app.models.user import UserRole, User

router = APIRouter()

admin_roles = RoleChecker([UserRole.SUPER_ADMIN, UserRole.HOSPITAL_ADMIN])

@router.get("/operational-metrics", response_model=OperationalMetricsSummary)
async def get_operational_analytics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(admin_roles)
):
    service = ReportsService(db)
    return await service.get_operational_summary()

@router.get("/financial-summary", response_model=FinancialSummary)
async def get_financial_analytics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(admin_roles)
):
    service = ReportsService(db)
    return await service.get_financial_summary()

@router.get("/fefo-expiry-alerts", response_model=FEFOExpiryAlertSummary)
async def get_fefo_expiry_report(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(admin_roles)
):
    service = ReportsService(db)
    return await service.get_fefo_expiry_alerts()
