# app/models/vitals.py
import uuid
from datetime import datetime
from sqlalchemy import Float, Integer, String, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

class PatientVitals(Base):
    __tablename__ = "patient_vitals"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False)
    recorded_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False) # Nurse / Doctor
    
    systolic_bp: Mapped[int | None] = mapped_column(Integer, nullable=True) # mmHg
    diastolic_bp: Mapped[int | None] = mapped_column(Integer, nullable=True) # mmHg
    pulse_rate: Mapped[int | None] = mapped_column(Integer, nullable=True) # bpm
    temperature_f: Mapped[float | None] = mapped_column(Float, nullable=True) # Fahrenheit
    spo2_percent: Mapped[int | None] = mapped_column(Integer, nullable=True) # %
    weight_kg: Mapped[float | None] = mapped_column(Float, nullable=True) # kg
    height_cm: Mapped[float | None] = mapped_column(Float, nullable=True) # cm
    
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

# app/models/encounter.py
import uuid
from datetime import datetime
from sqlalchemy import String, Text, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

class ClinicalEncounter(Base):
    __tablename__ = "clinical_encounters"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    appointment_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("appointments.id"), nullable=False)
    patient_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False)
    doctor_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    vitals_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("patient_vitals.id"), nullable=True)
    
    chief_complaints: Mapped[str] = mapped_column(Text, nullable=False)
    history_of_present_illness: Mapped[str | None] = mapped_column(Text, nullable=True)
    physical_examination: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    icd10_code: Mapped[str | None] = mapped_column(String(20), nullable=True) # e.g. "J06.9"
    diagnosis_notes: Mapped[str] = mapped_column(Text, nullable=False)
    
    advice_and_plan: Mapped[str | None] = mapped_column(Text, nullable=True)
    follow_up_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

# app/models/prescription.py
import uuid
from datetime import datetime
from sqlalchemy import String, Integer, ForeignKey, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

class PrescriptionItem(Base):
    __tablename__ = "prescription_items"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    encounter_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("clinical_encounters.id"), nullable=False)
    
    medicine_name: Mapped[str] = mapped_column(String(150), nullable=False) # Generic or Brand Name
    dosage: Mapped[str] = mapped_column(String(50), nullable=False) # e.g. "500mg"
    frequency: Mapped[str] = mapped_column(String(50), nullable=False) # e.g. "1-0-1" (BD)
    duration_days: Mapped[int] = mapped_column(Integer, nullable=False)
    instructions: Mapped[str | None] = mapped_column(Text, nullable=True) # e.g. "After food (खानापछि)"
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
