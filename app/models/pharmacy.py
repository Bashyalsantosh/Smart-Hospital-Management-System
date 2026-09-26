import uuid
from datetime import datetime, date
from sqlalchemy import String, Integer, Float, Date, DateTime, Enum, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum
from app.core.database import Base

class TransactionType(str, enum.Enum):
    PURCHASE = "PURCHASE"
    DISPENSE = "DISPENSE"
    RETURN = "RETURN"
    ADJUSTMENT = "ADJUSTMENT"

class MedicineMaster(Base):
    __tablename__ = "medicine_masters"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    generic_name: Mapped[str] = mapped_column(String(150), index=True, nullable=False) # e.g., Paracetamol
    brand_name: Mapped[str] = mapped_column(String(150), index=True, nullable=False)   # e.g., Cetamol
    category: Mapped[str] = mapped_column(String(50), nullable=False)                 # e.g., Analgesic, Tablet
    reorder_level: Mapped[int] = mapped_column(Integer, default=100)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

class MedicineBatch(Base):
    __tablename__ = "medicine_batches"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    medicine_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("medicine_masters.id"), nullable=False)
    batch_number: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    expiry_date: Mapped[date] = mapped_column(Date, index=True, nullable=False)
    
    quantity_available: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    unit_purchase_price: Mapped[float] = mapped_column(Float, nullable=False)
    unit_selling_price: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

class PharmacyTransaction(Base):
    __tablename__ = "pharmacy_transactions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    batch_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("medicine_batches.id"), nullable=False)
    patient_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=True)
    performed_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    transaction_type: Mapped[TransactionType] = mapped_column(Enum(TransactionType), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    total_amount: Mapped[float] = mapped_column(Float, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    transaction_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
