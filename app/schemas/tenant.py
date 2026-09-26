from pydantic import BaseModel, EmailStr, Field
from uuid import UUID
from datetime import datetime

class HospitalTenantCreate(BaseModel):
    name: str = Field(..., example="Kathmandu City Hospital")
    code: str = Field(..., example="KCH-01")
    pan_vat_number: str = Field(..., example="600123456")
    address: str = Field(..., example="Tripureshwor, Kathmandu")
    phone_number: str = Field(..., example="+977-1-4200000")
    email: EmailStr = Field(..., example="info@kchospital.com.np")
    config: dict = Field(default={
        "tax_rate_percent": 13.0,
        "currency": "NPR",
        "invoice_header": "Kathmandu City Hospital Pvt. Ltd.",
        "invoice_footer": "Wish you a speedy recovery!"
    })

class HospitalTenantResponse(HospitalTenantCreate):
    id: UUID
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
