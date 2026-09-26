import uuid
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

class HospitalTenant(Base):
    __tablename__ = "hospital_tenants"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False) # e.g. "Kathmandu City Hospital - Main Branch"
    code: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False) # e.g. "KCH-MAIN"
    pan_vat_number: Mapped[str] = mapped_column(String(50), nullable=False)
    address: Mapped[str] = mapped_column(String(255), nullable=False)
    phone_number: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False)
    
    # Configuration Metadata (Header, Footer text, Tax Rates)
    config: Mapped[dict] = mapped_column(JSON, default={
        "tax_rate_percent": 13.0,
        "currency": "NPR",
        "invoice_header": "Kathmandu City Hospital Pvt. Ltd.",
        "invoice_footer": "Thank you for choosing Kathmandu City Hospital."
    }, nullable=False)
    
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
