from pydantic import BaseModel, Field
from datetime import date, datetime
from uuid import UUID
from app.models.pharmacy import TransactionType

class MedicineCreate(BaseModel):
    generic_name: str = Field(..., example="Paracetamol")
    brand_name: str = Field(..., example="Cetamol")
    category: str = Field(..., example="Tablet")
    reorder_level: int = Field(100, ge=0)

class MedicineResponse(MedicineCreate):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True

class BatchCreate(BaseModel):
    medicine_id: UUID
    batch_number: str = Field(..., example="B12026")
    expiry_date: date = Field(..., example="2027-12-31")
    quantity_available: int = Field(..., ge=1, example=500)
    unit_purchase_price: float = Field(..., gt=0, example=1.5)
    unit_selling_price: float = Field(..., gt=0, example=2.5)

class BatchResponse(BatchCreate):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True

class DispenseRequest(BaseModel):
    medicine_id: UUID
    patient_id: UUID | None = None
    quantity: int = Field(..., ge=1, example=10)

class DispenseSummary(BaseModel):
    batch_id: UUID
    batch_number: str
    expiry_date: date
    dispensed_quantity: int
    unit_price: float
    total_price: float
