from pydantic import BaseModel, EmailStr, Field
from datetime import date, datetime
from uuid import UUID
from app.models.patient import GenderEnum, BloodGroupEnum

class PatientCreate(BaseModel):
    first_name: str = Field(..., min_length=2, max_length=50, example="राम")
    last_name: str = Field(..., min_length=2, max_length=50, example="श्रेष्ठ")
    dob: date = Field(..., example="1995-04-12")
    gender: GenderEnum
    phone: str = Field(..., pattern=r"^\+?[0-9]{10,15}$", example="9841000000")
    email: EmailStr | None = None
    address: str = Field(..., example="काठमाडौँ-०३, बागमती")
    blood_group: BloodGroupEnum = BloodGroupEnum.UNKNOWN
    
    emergency_contact_name: str = Field(..., example="हरि श्रेष्ठ")
    emergency_contact_phone: str = Field(..., pattern=r"^\+?[0-9]{10,15}$", example="9801000000")
    emergency_contact_relation: str = Field(..., example="Brother")
    allergies_summary: str | None = None

class PatientResponse(BaseModel):
    id: UUID
    patient_code: str
    first_name: str
    last_name: str
    dob: date
    gender: GenderEnum
    phone: str
    email: EmailStr | None
    address: str
    blood_group: BloodGroupEnum
    emergency_contact_name: str
    emergency_contact_phone: str
    emergency_contact_relation: str
    allergies_summary: str | None
    created_at: datetime

    class Config:
        from_attributes = True

class DuplicateCheckResult(BaseModel):
    has_duplicates: bool
    matches: list[PatientResponse]
