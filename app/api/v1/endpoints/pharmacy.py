import uuid
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.pharmacy import MedicineCreate, MedicineResponse, BatchCreate, BatchResponse, DispenseRequest, DispenseSummary
from app.services.pharmacy_service import PharmacyService
from app.repositories.pharmacy_repo import PharmacyRepository
from app.api.deps import RoleChecker
from app.models.user import UserRole, User

router = APIRouter()

pharmacy_roles = RoleChecker([UserRole.PHARMACIST, UserRole.SUPER_ADMIN, UserRole.HOSPITAL_ADMIN])

@router.post("/medicines", response_model=MedicineResponse, status_code=status.HTTP_201_CREATED)
async def add_medicine_master(
    med_in: MedicineCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(pharmacy_roles)
):
    repo = PharmacyRepository(db)
    med = await repo.create_medicine(med_in)
    return MedicineResponse.model_validate(med)

@router.post("/batches", response_model=BatchResponse, status_code=status.HTTP_201_CREATED)
async def receive_stock_batch(
    batch_in: BatchCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(pharmacy_roles)
):
    repo = PharmacyRepository(db)
    batch = await repo.add_batch(batch_in)
    return BatchResponse.model_validate(batch)

@router.post("/dispense", response_model=List[DispenseSummary])
async def dispense_medicine(
    dispense_in: DispenseRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(pharmacy_roles)
):
    service = PharmacyService(db)
    return await service.dispense_medicine_fefo(dispense_in, current_user.id)
