import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.repositories.pharmacy_repo import PharmacyRepository
from app.schemas.pharmacy import DispenseRequest, DispenseSummary
from app.models.pharmacy import TransactionType

class PharmacyService:
    def __init__(self, db: AsyncSession):
        self.repo = PharmacyRepository(db)

    async def dispense_medicine_fefo(self, req: DispenseRequest, pharmacist_id: uuid.UUID) -> list[DispenseSummary]:
        batches = await self.repo.get_fefo_batches(req.medicine_id)
        
        total_available = sum(b.quantity_available for b in batches)
        if total_available < req.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient stock available. Required: {req.quantity}, Available: {total_available}"
            )

        remaining_qty = req.quantity
        dispense_breakdown: list[DispenseSummary] = []

        for batch in batches:
            if remaining_qty == 0:
                break

            deduct_qty = min(batch.quantity_available, remaining_qty)
            batch.quantity_available -= deduct_qty
            remaining_qty -= deduct_qty

            cost = deduct_qty * batch.unit_selling_price
            
            # Record audit transaction
            await self.repo.record_transaction(
                batch_id=batch.id,
                patient_id=req.patient_id,
                user_id=pharmacist_id,
                qty=deduct_qty,
                amount=cost,
                tx_type=TransactionType.DISPENSE
            )

            dispense_breakdown.append(DispenseSummary(
                batch_id=batch.id,
                batch_number=batch.batch_number,
                expiry_date=batch.expiry_date,
                dispensed_quantity=deduct_qty,
                unit_price=batch.unit_selling_price,
                total_price=cost
            ))

        await self.repo.db.flush()
        return dispense_breakdown
