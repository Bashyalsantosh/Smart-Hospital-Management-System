import uuid
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, or_, and_
from app.models.patient import Patient
from app.schemas.patient import PatientCreate

class PatientRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, patient_id: uuid.UUID) -> Patient | None:
        return await self.db.get(Patient, patient_id)

    async def get_by_code(self, patient_code: str) -> Patient | None:
        result = await self.db.execute(select(Patient).where(Patient.patient_code == patient_code))
        return result.scalars().first()

    async def count_patients_today(self) -> int:
        today = date.today()
        result = await self.db.execute(
            select(func.count(Patient.id)).where(func.date(Patient.created_at) == today)
        )
        return result.scalar() or 0

    async def find_possible_duplicates(self, phone: str, first_name: str, dob: date) -> list[Patient]:
        # Duplicate Rule: Phone matching OR (First Name AND DOB matching)
        stmt = select(Patient).where(
            or_(
                Patient.phone == phone,
                and_(
                    func.lower(Patient.first_name) == first_name.lower(),
                    Patient.dob == dob
                )
            )
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def create(self, patient_data: PatientCreate, generated_code: str) -> Patient:
        db_patient = Patient(
            **patient_data.model_dump(),
            patient_code=generated_code
        )
        self.db.add(db_patient)
        await self.db.flush()
        await self.db.refresh(db_patient)
        return db_patient

    async def search(self, query: str, limit: int = 20, offset: int = 0) -> list[Patient]:
        search_pattern = f"%{query}%"
        stmt = select(Patient).where(
            or_(
                Patient.patient_code.ilike(search_pattern),
                Patient.first_name.ilike(search_pattern),
                Patient.last_name.ilike(search_pattern),
                Patient.phone.ilike(search_pattern)
            )
        ).limit(limit).offset(offset)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
