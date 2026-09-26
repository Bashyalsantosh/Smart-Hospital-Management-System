# app/models/department.py
import uuid
from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

class Department(Base):
    __tablename__ = "departments"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False) # e.g., Cardiology, Orthopedics
    code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False) # e.g., CARD, ORTH

# app/models/doctor.py
import uuid
from sqlalchemy import String, ForeignKey, Time, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

class DoctorSchedule(Base):
    __tablename__ = "doctor_schedules"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    doctor_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    department_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("departments.id"), nullable=False)
    day_of_week: Mapped[int] = mapped_column(Integer, nullable=False) # 0=Sunday, 1=Monday... (Nepal Context: Sunday Start)
    start_time: Mapped[str] = mapped_column(String(10), nullable=False) # e.g., "09:00"
    end_time: Mapped[str] = mapped_column(String(10), nullable=False)   # e.g., "13:00"
    max_patients: Mapped[int] = mapped_column(Integer, default=30)

# app/models/appointment.py
import uuid
from datetime import datetime, date
from sqlalchemy import String, Date, DateTime, Enum, ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
import enum
from app.core.database import Base

class AppointmentStatus(str, enum.Enum):
    SCHEDULED = "SCHEDULED"
    CHECKED_IN = "CHECKED_IN"
    IN_CONSULTATION = "IN_CONSULTATION"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

class Appointment(Base):
    __tablename__ = "appointments"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    appointment_number: Mapped[str] = mapped_column(String(30), unique=True, nullable=False) # APP-20260926-001
    patient_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False)
    doctor_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    department_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("departments.id"), nullable=False)
    
    appointment_date: Mapped[date] = mapped_column(Date, nullable=False)
    nepali_date_bs: Mapped[str] = mapped_column(String(15), nullable=False) # e.g., "2083-06-10"
    token_number: Mapped[int] = mapped_column(Integer, nullable=False) # Daily Queue Sequence Token
    
    status: Mapped[AppointmentStatus] = mapped_column(Enum(AppointmentStatus), default=AppointmentStatus.SCHEDULED)
    chief_complaint: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
