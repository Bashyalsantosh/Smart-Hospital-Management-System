import uuid
import random
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.ipd import Ward, Bed, IPDAdmission, BedStatus, AdmissionStatus
from app.schemas.ipd import WardCreate, BedCreate, AdmissionCreate

class IPDRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_ward(self, ward_in: WardCreate) -> Ward:
        ward = Ward(**ward_in.model_dump())
        self.db.add(ward)
        await self.db.flush()
        await self.db.refresh(ward)
        return ward

    async def create_bed(self, bed_in: BedCreate) -> Bed:
        bed = Bed(**bed_in.model_dump(), status=BedStatus.AVAILABLE)
        self.db.add(bed)
        await self.db.flush()
        await self.db.refresh(bed)
        return bed

    async def create_admission(self, adm_in: AdmissionCreate) -> IPDAdmission:
        # Check and occupy bed
        bed = await self.db.get(Bed, adm_in.bed_id)
        if not bed or bed.status != BedStatus.AVAILABLE:
            raise ValueError("Selected Bed is not available")

        bed.status = BedStatus.OCCUPIED
        ipd_num = f"IPD-2083-{random.randint(1000, 9999)}"
        
        admission = IPDAdmission(
            ipd_number=ipd_num,
            patient_id=adm_in.patient_id,
            admitting_doctor_id=adm_in.admitting_doctor_id,
            bed_id=adm_in.bed_id,
            provisional_diagnosis=adm_in.provisional_diagnosis,
            status=AdmissionStatus.ADMITTED
        )
        self.db.add(admission)
        await self.db.flush()
        await self.db.refresh(admission)
        return admission

    async def process_discharge(
        self, admission_id: uuid.UUID, summary: str, advice: str
    ) -> IPDAdmission | None:
        admission = await self.db.get(IPDAdmission, admission_id)
        if not admission or admission.status != AdmissionStatus.ADMITTED:
            return None

        admission.status = AdmissionStatus.DISCHARGED
        admission.discharge_date = datetime.utcnow()
        admission.discharge_summary = summary
        admission.advice_on_discharge = advice

        # Free up the bed
        bed = await self.db.get(Bed, admission.bed_id)
        if bed:
            bed.status = BedStatus.AVAILABLE

        await self.db.flush()
        await self.db.refresh(admission)
        return admission
