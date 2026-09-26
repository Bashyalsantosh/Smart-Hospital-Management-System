from pydantic import BaseModel, Field
from datetime import datetime, date
from uuid import UUID

class VitalsCreate(BaseModel):
    patient_id: UUID
    systolic_bp: int | None = Field(None, ge=50, le=250, example=120)
    diastolic_bp: int | None = Field(None, ge=30, le=150, example=80)
    pulse_rate: int | None = Field(None, ge=30, le=220, example=72)
    temperature_f: float | None = Field(None, ge=90.0, le=110.0, example=98.6)
    spo2_percent: int | None = Field(None, ge=50, le=100, example=98)
    weight_kg: float | None = Field(None, ge=1.0, le=300.0, example=65.5)
    height_cm: float | None = Field(None, ge=30.0, le=250.0, example=170.0)

class VitalsResponse(VitalsCreate):
    id: UUID
    recorded_by: UUID
    recorded_at: datetime

    class Config:
        from_attributes = True

class PrescriptionItemCreate(BaseModel):
    medicine_name: str = Field(..., example="Paracetamol")
    dosage: str = Field(..., example="500mg")
    frequency: str = Field(..., example="1-0-1")
    duration_days: int = Field(..., ge=1, example=5)
    instructions: str | None = Field(None, example="खानापछि सेवान गर्ने")

class PrescriptionItemResponse(PrescriptionItemCreate):
    id: UUID
    encounter_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True

class EncounterCreate(BaseModel):
    appointment_id: UUID
    patient_id: UUID
    vitals_id: UUID | None = None
    chief_complaints: str = Field(..., example="Fever and Cough for 3 days")
    history_of_present_illness: str | None = None
    physical_examination: str | None = None
    icd10_code: str | None = Field(None, example="J06.9")
    diagnosis_notes: str = Field(..., example="Acute Upper Respiratory Tract Infection")
    advice_and_plan: str | None = None
    follow_up_date: date | None = None
    prescriptions: list[PrescriptionItemCreate] = []

class EncounterResponse(BaseModel):
    id: UUID
    appointment_id: UUID
    patient_id: UUID
    doctor_id: UUID
    vitals_id: UUID | None
    chief_complaints: str
    icd10_code: str | None
    diagnosis_notes: str
    advice_and_plan: str | None
    follow_up_date: datetime | None
    created_at: datetime
    prescriptions: list[PrescriptionItemResponse] = []

    class Config:
        from_attributes = True
