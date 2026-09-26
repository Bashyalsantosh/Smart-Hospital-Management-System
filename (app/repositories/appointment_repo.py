import uuid
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, and_
from app.models.appointment import Appointment, AppointmentStatus
from app.schemas.appointment import AppointmentCreate

class AppointmentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_next_token_number(self, doctor_id: uuid.UUID, appt_date: date) -> int:
        stmt = select(func.max(Appointment.token_number)).where(
            and_(
                Appointment.doctor_id == doctor_id,
                Appointment.appointment_date == appt_date
            )
        )
        result = await self.db.execute(stmt)
        max_token = result.scalar()
        return (max_token or 0) + 1

    async def create(self, appt_in: AppointmentCreate, appt_num: str, token: int) -> Appointment:
        db_appt = Appointment(
            **appt_in.model_dump(),
            appointment_number=appt_num,
            token_number=token
        )
        self.db.add(db_appt)
        await self.db.flush()
        await self.db.refresh(db_appt)
        return db_appt

    async def get_today_queue(self, doctor_id: uuid.UUID, appt_date: date) -> list[Appointment]:
        stmt = select(Appointment).where(
            and_(
                Appointment.doctor_id == doctor_id,
                Appointment.appointment_date == appt_date,
                Appointment.status != AppointmentStatus.CANCELLED
            )
        ).order_by(Appointment.token_number.asc())
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
