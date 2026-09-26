import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.emr_repo import EMRRepository
from app.schemas.emr import VitalsCreate, VitalsResponse, EncounterCreate, EncounterResponse, PrescriptionItemResponse

class EMRService:
    def __init__(self, db: AsyncSession):
        self.repo = EMRRepository(db)

    async def record_vitals(self, vitals_in: VitalsCreate, recorder_id: uuid.UUID) -> VitalsResponse:
        vitals = await self.repo.create_vitals(vitals_in, recorder_id)
        return VitalsResponse.model_validate(vitals)

    async def create_clinical_encounter(self, enc_in: EncounterCreate, doctor_id: uuid.UUID) -> EncounterResponse:
        encounter = await self.repo.create_encounter(enc_in, doctor_id)
        rx_items = await self.repo.get_prescriptions_for_encounter(encounter.id)
        
        response = EncounterResponse.model_validate(encounter)
        response.prescriptions = [PrescriptionItemResponse.model_validate(p) for p in rx_items]
        return response

    async def get_full_patient_emr(self, patient_id: uuid.UUID) -> list[EncounterResponse]:
        encounters = await self.repo.get_patient_history(patient_id)
        results = []
        for enc in encounters:
            rx_items = await self.repo.get_prescriptions_for_encounter(enc.id)
            resp = EncounterResponse.model_validate(enc)
            resp.prescriptions = [PrescriptionItemResponse.model_validate(p) for p in rx_items]
            results.append(resp)
        return results
