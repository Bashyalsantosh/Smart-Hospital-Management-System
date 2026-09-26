import uuid
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.ipd import WardCreate, WardResponse, BedCreate, BedResponse, AdmissionCreate, IPDAdmissionResponse, DischargeRequest
from app.services.ipd_service import IPDService
from app.repositories.ipd_repo import IPDRepository
from app.api.deps import RoleChecker
from app.models.user import UserRole, User

router = APIRouter()

admin_and_nurse_roles = RoleChecker([UserRole.NURSE, UserRole.DOCTOR, UserRole.SUPER_ADMIN, UserRole.HOSPITAL_ADMIN])
doctor_roles = RoleChecker([UserRole.DOCTOR, UserRole.SUPER_ADMIN])

@router.post("/wards", response_model=WardResponse, status_code=status.HTTP_201_CREATED)
async def create_hospital_ward(
    ward_in: WardCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(admin_and_nurse_roles)
):
    repo = IPDRepository(db)
    ward = await repo.create_ward(ward_in)
    return WardResponse.model_validate(ward)

@router.post("/beds", response_model=BedResponse, status_code=status.HTTP_201_CREATED)
async def add_ward_bed(
    bed_in: BedCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(admin_and_nurse_roles)
):
    repo = IPDRepository(db)
    bed = await repo.create_bed(bed_in)
    return BedResponse.model_validate(bed)

@router.post("/admit", response_model=IPDAdmissionResponse, status_code=status.HTTP_201_CREATED)
async def admit_patient_to_ipd(
    adm_in: AdmissionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(admin_and_nurse_roles)
):
    service = IPDService(db)
    return await service.admit_patient(adm_in)

@router.post("/admissions/{admission_id}/discharge", response_model=IPDAdmissionResponse)
async def discharge_ipd_patient(
    admission_id: uuid.UUID,
    discharge_in: DischargeRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(doctor_roles)
):
    service = IPDService(db)
    return await service.discharge_patient(admission_id, discharge_in)
