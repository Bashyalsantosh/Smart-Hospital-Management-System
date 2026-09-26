import uuid
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_
from app.models.pharmacy import MedicineMaster, MedicineBatch, PharmacyTransaction, TransactionType
from app.schemas.pharmacy import MedicineCreate, BatchCreate

class PharmacyRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_medicine(self, med_in: MedicineCreate) -> MedicineMaster:
        med = MedicineMaster(**med_in.model_dump())
        self.db.add(med)
        await self.db.flush()
        await self.db.refresh(med)
        return med

    async def add_batch(self, batch_in: BatchCreate) -> MedicineBatch:
        batch = MedicineBatch(**batch_in.model_dump())
        self.db.add(batch)
        await self.db.flush()
        await self.db.refresh(batch)
        return batch

    async def get_fefo_batches(self, medicine_id: uuid.UUID) -> list[MedicineBatch]:
        """
        FEFO Logic: 
        1. Select non-expired batches for the medicine
        2. Filter quantity_available > 0
        3. ORDER BY expiry_date ASC (earliest expiring stock first)
        """
        today = date.today()
        stmt = select(MedicineBatch).where(
            and_(
                MedicineBatch.medicine_id == medicine_id,
                MedicineBatch.quantity_available > 0,
                MedicineBatch.expiry_date > today
            )
        ).order_by(MedicineBatch.expiry_date.asc())
        
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def record_transaction(
        self, batch_id: uuid.UUID, patient_id: uuid.UUID | None, 
        user_id: uuid.UUID, qty: int, amount: float, tx_type: TransactionType
    ):
        tx = PharmacyTransaction(
            batch_id=batch_id,
            patient_id=patient_id,
            performed_by=user_id,
            transaction_type=tx_type,
            quantity=qty,
            total_amount=amount
        )
        self.db.add(tx)
