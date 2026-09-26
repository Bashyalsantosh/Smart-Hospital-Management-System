from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID
from app.models.ipd import BedStatus, AdmissionStatus

class WardCreate(BaseModel):
    ward_name: str = Field(..., example="ICU Ward")
    ward_type: str = Field(..., example="ICU")
    daily_charge: float = Field(..., gt=0, example=3500.0)

class WardResponse(WardCreate):
    id: UUID

    class Config:
        from_attributes = True

class BedCreate(BaseModel):
    ward_id: UUID
    bed_number: str = Field(..., example="ICU-01")

class BedResponse(BedCreate):
    id: UUID
    status: BedStatus

    class Config:
        from_attributes = True

class AdmissionCreate(BaseModel):
    patient_id: UUID
    admitting_doctor_id: UUID
    bed_id: UUID
    provisional_diagnosis: str = Field(..., example="Acute Appendicitis with Localized Peritonitis")

class DischargeRequest(BaseModel):
    discharge_summary: str = Field(..., example="Patient underwent emergency laparoscopic appendectomy. Post-op recovery uneventful.")
    advice_on_discharge: str = Field(..., example="Rest for 2 weeks, avoid heavy lifting. Follow up after 7 days.")

class IPDAdmissionResponse(BaseModel):
    id: UUID
    ipd_number: str
    patient_id: UUID
    admitting_doctor_id: UUID
    bed_id: UUID
    admission_date: datetime
    discharge_date: datetime | None
    provisional_diagnosis: str
    status: AdmissionStatus
    discharge_summary: str | None
    advice_on_discharge: str | None

    class Config:
        from_attributes = True
