import uuid
from datetime import datetime
from sqlalchemy import String, Float, ForeignKey, DateTime, Enum, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
import enum
from app.core.database import Base

class TestOrderStatus(str, enum.Enum):
    ORDERED = "ORDERED"
    SAMPLE_COLLECTED = "SAMPLE_COLLECTED"
    IN_ANALYSIS = "IN_ANALYSIS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

class LabTestMaster(Base):
    __tablename__ = "lab_test_masters"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    test_code: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False) # e.g. "CBC", "LFT"
    test_name: Mapped[str] = mapped_column(String(150), nullable=False)                         # e.g. "Complete Blood Count"
    category: Mapped[str] = mapped_column(String(100), nullable=False)                        # e.g. "Hematology"
    price: Mapped[float] = mapped_column(Float, nullable=False)
    sample_type: Mapped[str] = mapped_column(String(100), nullable=False)                      # e.g. "EDTA Whole Blood"
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

class LabOrder(Base):
    __tablename__ = "lab_orders"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False)
    encounter_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("clinical_encounters.id"), nullable=True)
    ordered_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    test_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("lab_test_masters.id"), nullable=False)
    status: Mapped[TestOrderStatus] = mapped_column(Enum(TestOrderStatus), default=TestOrderStatus.ORDERED, nullable=False)
    sample_barcode: Mapped[str | None] = mapped_column(String(100), unique=True, nullable=True)
    
    ordered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

class LabResult(Base):
    __tablename__ = "lab_results"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lab_order_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("lab_orders.id"), nullable=False)
    parameter_name: Mapped[str] = mapped_column(String(100), nullable=False)  # e.g. "Hemoglobin"
    result_value: Mapped[str] = mapped_column(String(100), nullable=False)    # e.g. "13.5"
    unit: Mapped[str | None] = mapped_column(String(50), nullable=True)        # e.g. "g/dL"
    reference_range: Mapped[str | None] = mapped_column(String(100), nullable=True) # e.g. "12.0 - 16.0"
    is_abnormal: Mapped[bool] = mapped_column(Boolean, default=False)
    
    entered_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    approved_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
