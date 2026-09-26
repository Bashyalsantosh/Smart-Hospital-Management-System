import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.repositories.ipd_repo import IPDRepository
from app.schemas.ipd import AdmissionCreate, IPDAdmissionResponse, DischargeRequest

class IPDService:
    def __init__(self, db: AsyncSession):
        self.repo = IPDRepository(db)

    async def admit_patient(self, adm_in: AdmissionCreate) -> IPDAdmissionResponse:
        try:
            admission = await self.repo.create_admission(adm_in)
            return IPDAdmissionResponse.model_validate(admission)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    async def discharge_patient(
        self, admission_id: uuid.UUID, discharge_in: DischargeRequest
    ) -> IPDAdmissionResponse:
        admission = await self.repo.process_discharge(
            admission_id, discharge_in.discharge_summary, discharge_in.advice_on_discharge
        )
        if not admission:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid IPD Admission record or patient already discharged"
            )
        return IPDAdmissionResponse.model_validate(admission)
