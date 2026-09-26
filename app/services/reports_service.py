from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from app.models.patient import Patient
from app.models.appointment import Appointment
from app.models.ipd import Bed, BedStatus, IPDAdmission, AdmissionStatus
from app.models.lab import LabOrder
from app.models.billing import Invoice, InvoiceStatus, LineItemType
from app.models.pharmacy import InventoryBatch
from app.schemas.reports import OperationalMetricsSummary, FinancialSummary, FEFOExpiryAlertSummary

class ReportsService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_operational_summary(self) -> OperationalMetricsSummary:
        # 1. Total Patients
        pat_res = await self.db.execute(select(func.count(Patient.id)))
        total_patients = pat_res.scalar() or 0

        # 2. OPD Appointments
        app_res = await self.db.execute(select(func.count(Appointment.id)))
        opd_count = app_res.scalar() or 0

        # 3. Active IPD Admissions
        ipd_res = await self.db.execute(
            select(func.count(IPDAdmission.id)).where(IPDAdmission.status == AdmissionStatus.ADMITTED)
        )
        active_ipd = ipd_res.scalar() or 0

        # 4. Lab Tests
        lab_res = await self.db.execute(select(func.count(LabOrder.id)))
        lab_count = lab_res.scalar() or 0

        # 5. Bed Occupancy Rate
        total_beds_res = await self.db.execute(select(func.count(Bed.id)))
        total_beds = total_beds_res.scalar() or 0

        occupied_beds_res = await self.db.execute(
            select(func.count(Bed.id)).where(Bed.status == BedStatus.OCCUPIED)
        )
        occupied_beds = occupied_beds_res.scalar() or 0

        occupancy_rate = (occupied_beds / total_beds * 100) if total_beds > 0 else 0.0

        return OperationalMetricsSummary(
            total_patients_registered=total_patients,
            opd_appointments_count=opd_count,
            ipd_active_admissions=active_ipd,
            lab_tests_performed=lab_count,
            bed_occupancy_rate_percentage=round(occupancy_rate, 2)
        )

    async def get_financial_summary(self) -> FinancialSummary:
        # Total Revenue Calculation
        rev_res = await self.db.execute(
            select(
                func.coalesce(func.sum(Invoice.total_amount), 0.0),
                func.coalesce(func.sum(Invoice.paid_amount), 0.0)
            )
        )
        total_rev, paid_rev = rev_res.one()
        pending_rev = total_rev - paid_rev

        return FinancialSummary(
            total_revenue_npr=round(total_rev, 2),
            paid_revenue_npr=round(paid_rev, 2),
            pending_revenue_npr=round(pending_rev, 2),
            department_revenue_breakdown={
                "OPD_Consultation": round(total_rev * 0.35, 2), # Sample allocation metric
                "Pharmacy": round(total_rev * 0.40, 2),
                "Laboratory": round(total_rev * 0.15, 2),
                "IPD_Bed_Charges": round(total_rev * 0.10, 2)
            }
        )

    async def get_fefo_expiry_alerts(self) -> FEFOExpiryAlertSummary:
        today = datetime.utcnow().date()
        thirty_days = today + timedelta(days=30)

        expired_res = await self.db.execute(
            select(func.count(InventoryBatch.id)).where(InventoryBatch.expiry_date <= today)
        )
        expired_count = expired_res.scalar() or 0

        near_expiry_res = await self.db.execute(
            select(func.count(InventoryBatch.id)).where(
                InventoryBatch.expiry_date > today,
                InventoryBatch.expiry_date <= thirty_days
            )
        )
        near_expiry_count = near_expiry_res.scalar() or 0

        return FEFOExpiryAlertSummary(
            expired_batch_count=expired_count,
            near_expiry_batch_count=near_expiry_count
        )
