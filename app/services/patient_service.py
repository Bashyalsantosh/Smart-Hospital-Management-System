from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.repositories.patient_repo import PatientRepository
from app.schemas.patient import PatientCreate, PatientResponse, DuplicateCheckResult

class PatientService:
    def __init__(self, db: AsyncSession):
        self.repo = PatientRepository(db)

    async def generate_patient_code(self) -> str:
        # Code Format: HND-YYYYMMDD-XXXX (e.g. HND-20260926-0001)
        today_str = datetime.utcnow().strftime("%Y%m%d")
        daily_count = await self.repo.count_patients_today() + 1
        return f"HND-{today_str}-{daily_count:04d}"

    async def check_duplicates(self, patient_data: PatientCreate) -> DuplicateCheckResult:
        matches = await self.repo.find_possible_duplicates(
            phone=patient_data.phone,
            first_name=patient_data.first_name,
            dob=patient_data.dob
        )
        matched_responses = [PatientResponse.model_validate(p) for p in matches]
        return DuplicateCheckResult(
            has_duplicates=len(matches) > 0,
            matches=matched_responses
        )

    async def register_patient(self, patient_data: PatientCreate, force_register: bool = False) -> PatientResponse:
        if not force_register:
            dup_result = await self.check_duplicates(patient_data)
            if dup_result.has_duplicates:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Possible duplicate patient detected. Review duplicates or pass force_register=True."
                )

        patient_code = await self.generate_patient_code()
        new_patient = await self.repo.create(patient_data, patient_code)
        return PatientResponse.model_validate(new_patient)
