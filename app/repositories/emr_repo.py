import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.models.vitals import PatientVitals
from app.models.encounter import ClinicalEncounter
from app.models.prescription import PrescriptionItem
from app.models.appointment import Appointment, AppointmentStatus
from app.schemas.emr import VitalsCreate, EncounterCreate

class EMRRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_vitals(self, vitals_in: VitalsCreate, recorder_id: uuid.UUID) -> PatientVitals:
        vitals = PatientVitals(**vitals_in.model_dump(), recorded_by=recorder_id)
        self.db.add(vitals)
        await self.db.flush()
        await self.db.refresh(vitals)
        return vitals

    async def create_encounter(self, enc_in: EncounterCreate, doctor_id: uuid.UUID) -> ClinicalEncounter:
        data = enc_in.model_dump()
        prescriptions_data = data.pop("prescriptions", [])

        # 1. Create Encounter
        encounter = ClinicalEncounter(**data, doctor_id=doctor_id)
        self.db.add(encounter)
        await self.db.flush()

        # 2. Add Prescription Items
        for p_data in prescriptions_data:
            rx_item = PrescriptionItem(**p_data, encounter_id=encounter.id)
            self.db.add(rx_item)

        # 3. Update Appointment Status to COMPLETED
        appt = await self.db.get(Appointment, enc_in.appointment_id)
        if appt:
            appt.status = AppointmentStatus.COMPLETED

        await self.db.flush()
        await self.db.refresh(encounter)
        return encounter

    async def get_patient_history(self, patient_id: uuid.UUID) -> list[ClinicalEncounter]:
        stmt = select(ClinicalEncounter).where(
            ClinicalEncounter.patient_id == patient_id
        ).order_by(ClinicalEncounter.created_at.desc())
        
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_prescriptions_for_encounter(self, encounter_id: uuid.UUID) -> list[PrescriptionItem]:
        stmt = select(PrescriptionItem).where(PrescriptionItem.encounter_id == encounter_id)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
