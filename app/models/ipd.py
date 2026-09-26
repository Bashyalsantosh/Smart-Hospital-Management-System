import uuid
from datetime import datetime
from sqlalchemy import String, Float, Integer, ForeignKey, DateTime, Enum, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
import enum
from app.core.database import Base

class BedStatus(str, enum.Enum):
    AVAILABLE = "AVAILABLE"
    OCCUPIED = "OCCUPIED"
    MAINTENANCE = "MAINTENANCE"
    RESERVED = "RESERVED"

class AdmissionStatus(str, enum.Enum):
    ADMITTED = "ADMITTED"
    DISCHARGED = "DISCHARGED"
    TRANSFERRED = "TRANSFERRED"
    LAMA = "LAMA" # Left Against Medical Advice

class Ward(Base):
    __tablename__ = "wards"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ward_name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False) # e.g. "General Male Ward", "ICU", "Cabin 101"
    ward_type: Mapped[str] = mapped_column(String(50), nullable=False)               # e.g. "GENERAL", "ICU", "CABIN", "NICU"
    daily_charge: Mapped[float] = mapped_column(Float, nullable=False)

class Bed(Base):
    __tablename__ = "beds"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ward_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("wards.id"), nullable=False)
    bed_number: Mapped[str] = mapped_column(String(50), nullable=False) # e.g. "BED-01", "ICU-02"
    status: Mapped[BedStatus] = mapped_column(Enum(BedStatus), default=BedStatus.AVAILABLE, nullable=False)

class IPDAdmission(Base):
    __tablename__ = "ipd_admissions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ipd_number: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False) # e.g. IPD-2083-0042
    patient_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False)
    admitting_doctor_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    bed_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("beds.id"), nullable=False)
    
    admission_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    discharge_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    
    provisional_diagnosis: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[AdmissionStatus] = mapped_column(Enum(AdmissionStatus), default=AdmissionStatus.ADMITTED, nullable=False)
    
    # Discharge Details
    discharge_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    advice_on_discharge: Mapped[str | None] = mapped_column(Text, nullable=True)
