import uuid
from typing import List
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.emr import VitalsCreate, VitalsResponse, EncounterCreate, EncounterResponse
from app.services.emr_service import EMRService
from app.api.deps import RoleChecker, get_current_user
from app.models.user import UserRole, User

router = APIRouter()

nurse_and_doctor_roles = RoleChecker([UserRole.NURSE, UserRole.DOCTOR, UserRole.SUPER_ADMIN])
doctor_only_roles = RoleChecker([UserRole.DOCTOR, UserRole.SUPER_ADMIN])
clinical_viewers = RoleChecker([UserRole.DOCTOR, UserRole.NURSE, UserRole.PHARMACIST, UserRole.SUPER_ADMIN])

@router.post("/vitals", response_model=VitalsResponse, status_code=status.HTTP_201_CREATED)
async def record_patient_vitals(
    vitals_in: VitalsCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(nurse_and_doctor_roles)
):
    service = EMRService(db)
    return await service.record_vitals(vitals_in, current_user.id)

@router.post("/consultation", response_model=EncounterResponse, status_code=status.HTTP_201_CREATED)
async def submit_consultation(
    encounter_in: EncounterCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(doctor_only_roles)
):
    service = EMRService(db)
    return await service.create_clinical_encounter(encounter_in, current_user.id)

@router.get("/patient/{patient_id}/history", response_model=List[EncounterResponse])
async def get_patient_emr_history(
    patient_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(clinical_viewers)
):
    service = EMRService(db)
    return await service.get_full_patient_emr(patient_id)
