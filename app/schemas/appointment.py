from pydantic import BaseModel, Field
from datetime import date, datetime
from uuid import UUID
from app.models.appointment import AppointmentStatus

class AppointmentCreate(BaseModel):
    patient_id: UUID
    doctor_id: UUID
    department_id: UUID
    appointment_date: date = Field(..., example="2026-09-27")
    nepali_date_bs: str = Field(..., example="2083-06-11")
    chief_complaint: str | None = None

class AppointmentResponse(BaseModel):
    id: UUID
    appointment_number: str
    patient_id: UUID
    doctor_id: UUID
    department_id: UUID
    appointment_date: date
    nepali_date_bs: str
    token_number: int
    status: AppointmentStatus
    chief_complaint: str | None
    created_at: datetime

    class Config:
        from_attributes = True
