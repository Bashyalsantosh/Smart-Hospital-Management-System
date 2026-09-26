import uuid
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.lab import LabTestMasterCreate, LabTestMasterResponse, LabOrderCreate, LabOrderResponse, LabResultEntry
from app.services.lab_service import LabService
from app.repositories.lab_repo import LabRepository
from app.api.deps import RoleChecker
from app.models.user import UserRole, User

router = APIRouter()

lab_tech_roles = RoleChecker([UserRole.LAB_TECHNICIAN, UserRole.SUPER_ADMIN])
clinical_roles = RoleChecker([UserRole.DOCTOR, UserRole.NURSE, UserRole.LAB_TECHNICIAN, UserRole.SUPER_ADMIN])

@router.post("/test-catalog", response_model=LabTestMasterResponse, status_code=status.HTTP_201_CREATED)
async def create_lab_test_item(
    test_in: LabTestMasterCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(lab_tech_roles)
):
    repo = LabRepository(db)
    test_item = await repo.create_test_master(test_in)
    return LabTestMasterResponse.model_validate(test_item)

@router.post("/orders", response_model=LabOrderResponse, status_code=status.HTTP_201_CREATED)
async def order_lab_test(
    order_in: LabOrderCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(clinical_roles)
):
    service = LabService(db)
    return await service.place_order(order_in, current_user.id)

@router.patch("/orders/{order_id}/collect-sample", response_model=LabOrderResponse)
async def collect_sample(
    order_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(lab_tech_roles)
):
    service = LabService(db)
    return await service.process_sample_collection(order_id)

@router.post("/orders/{order_id}/results", response_model=LabOrderResponse)
async def enter_lab_results(
    order_id: uuid.UUID,
    results_in: List[LabResultEntry],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(lab_tech_roles)
):
    service = LabService(db)
    return await service.submit_test_results(order_id, results_in, current_user.id)
