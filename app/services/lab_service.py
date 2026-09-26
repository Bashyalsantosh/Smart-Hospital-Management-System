import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.repositories.lab_repo import LabRepository
from app.schemas.lab import LabOrderCreate, LabOrderResponse, LabResultEntry, LabResultResponse

class LabService:
    def __init__(self, db: AsyncSession):
        self.repo = LabRepository(db)

    async def place_order(self, order_in: LabOrderCreate, doctor_id: uuid.UUID) -> LabOrderResponse:
        order = await self.repo.create_order(order_in, doctor_id)
        return LabOrderResponse.model_validate(order)

    async def process_sample_collection(self, order_id: uuid.UUID) -> LabOrderResponse:
        order = await self.repo.collect_specimen(order_id)
        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lab Order not found")
        return LabOrderResponse.model_validate(order)

    async def submit_test_results(
        self, order_id: uuid.UUID, results_in: list[LabResultEntry], tech_id: uuid.UUID
    ) -> LabOrderResponse:
        results = await self.repo.add_results(order_id, results_in, tech_id)
        if not results:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unable to submit results")

        stmt_order = await self.repo.db.get(self.repo.db.get_entity_range()[0], order_id) if hasattr(self.repo.db, 'get_entity_range') else None
        order = await self.repo.db.get(self.repo.create_order.__annotations__['return'], order_id) if hasattr(self.repo, 'create_order') else None
        
        # Reload Lab Order with Results
        from app.models.lab import LabOrder
        order_obj = await self.repo.db.get(LabOrder, order_id)
        
        response = LabOrderResponse.model_validate(order_obj)
        response.results = [LabResultResponse.model_validate(r) for r in results]
        return response
