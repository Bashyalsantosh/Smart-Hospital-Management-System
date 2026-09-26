import uuid
from typing import List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.patient import PatientCreate, PatientResponse, DuplicateCheckResult
from app.services.patient_service import PatientService
from app.repositories.patient_repo import PatientRepository
from app.api.deps import RoleChecker
from app.models.user import UserRole, User

router = APIRouter()

# Allow Receptionists, Admins, Doctors & Nurses to view/create patients
clinical_admin_roles = RoleChecker([
    UserRole.RECEPTIONIST, 
    UserRole.HOSPITAL_ADMIN, 
    UserRole.DOCTOR, 
    UserRole.NURSE,
    UserRole.SUPER_ADMIN
])

@router.post("/check-duplicates", response_model=DuplicateCheckResult)
async def check_patient_duplicates(
    patient_in: PatientCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(clinical_admin_roles)
):
    service = PatientService(db)
    return await service.check_duplicates(patient_in)

@router.post("/", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
async def register_patient(
    patient_in: PatientCreate,
    force_register: bool = Query(False, description="Bypass duplicate warnings"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(clinical_admin_roles)
):
    service = PatientService(db)
    return await service.register_patient(patient_in, force_register=force_register)

@router.get("/search", response_model=List[PatientResponse])
async def search_patients(
    q: str = Query(..., min_length=2, description="Search by Code, Name, or Phone"),
    limit: int = Query(20, le=100),
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(clinical_admin_roles)
):
    repo = PatientRepository(db)
    patients = await repo.search(q, limit=limit, offset=offset)
    return [PatientResponse.model_validate(p) for p in patients]

@router.get("/{patient_id}", response_model=PatientResponse)
async def get_patient_by_id(
    patient_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(clinical_admin_roles)
):
    repo = PatientRepository(db)
    patient = await repo.get_by_id(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient record not found")
    return PatientResponse.model_validate(patient)
