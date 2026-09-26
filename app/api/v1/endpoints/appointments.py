import uuid
from datetime import date
from typing import List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.appointment import AppointmentCreate, AppointmentResponse
from app.services.appointment_service import AppointmentService
from app.repositories.appointment_repo import AppointmentRepository
from app.api.deps import RoleChecker
from app.models.user import UserRole, User

router = APIRouter()

allowed_booking_roles = RoleChecker([
    UserRole.RECEPTIONIST, UserRole.PATIENT, UserRole.HOSPITAL_ADMIN, UserRole.DOCTOR
])

@router.post("/", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED)
async def book_appointment(
    appt_in: AppointmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(allowed_booking_roles)
):
    service = AppointmentService(db)
    return await service.book_appointment(appt_in)

@router.get("/queue/{doctor_id}", response_model=List[AppointmentResponse])
async def get_doctor_queue(
    doctor_id: uuid.UUID,
    target_date: date = Query(default=date.today()),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(allowed_booking_roles)
):
    repo = AppointmentRepository(db)
    appointments = await repo.get_today_queue(doctor_id, target_date)
    return [AppointmentResponse.model_validate(a) for a in appointments]
