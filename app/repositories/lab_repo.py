import uuid
import random
import string
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.lab import LabTestMaster, LabOrder, LabResult, TestOrderStatus
from app.schemas.lab import LabTestMasterCreate, LabOrderCreate, LabResultEntry

class LabRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_test_master(self, test_in: LabTestMasterCreate) -> LabTestMaster:
        test_master = LabTestMaster(**test_in.model_dump())
        self.db.add(test_master)
        await self.db.flush()
        await self.db.refresh(test_master)
        return test_master

    async def create_order(self, order_in: LabOrderCreate, doctor_id: uuid.UUID) -> LabOrder:
        order = LabOrder(
            patient_id=order_in.patient_id,
            encounter_id=order_in.encounter_id,
            test_id=order_in.test_id,
            ordered_by=doctor_id,
            status=TestOrderStatus.ORDERED
        )
        self.db.add(order)
        await self.db.flush()
        await self.db.refresh(order)
        return order

    async def collect_specimen(self, order_id: uuid.UUID) -> LabOrder | None:
        order = await self.db.get(LabOrder, order_id)
        if order:
            # Generate Unique Barcode String e.g. LAB-88A92B
            barcode_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            order.sample_barcode = f"LAB-{barcode_suffix}"
            order.status = TestOrderStatus.SAMPLE_COLLECTED
            await self.db.flush()
            await self.db.refresh(order)
        return order

    async def add_results(
        self, order_id: uuid.UUID, results_in: list[LabResultEntry], technician_id: uuid.UUID
    ) -> list[LabResult]:
        order = await self.db.get(LabOrder, order_id)
        if not order:
            return []

        created_results = []
        for r_in in results_in:
            result = LabResult(
                lab_order_id=order_id,
                parameter_name=r_in.parameter_name,
                result_value=r_in.result_value,
                unit=r_in.unit,
                reference_range=r_in.reference_range,
                is_abnormal=r_in.is_abnormal,
                entered_by=technician_id
            )
            self.db.add(result)
            created_results.append(result)

        order.status = TestOrderStatus.COMPLETED
        await self.db.flush()
        return created_results

    async def get_results_for_order(self, order_id: uuid.UUID) -> list[LabResult]:
        stmt = select(LabResult).where(LabResult.lab_order_id == order_id)
        res = await self.db.execute(stmt)
        return list(res.scalars().all())
