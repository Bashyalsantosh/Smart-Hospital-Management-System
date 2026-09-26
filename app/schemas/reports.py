from pydantic import BaseModel
from typing import List, Dict

class OperationalMetricsSummary(BaseModel):
    total_patients_registered: int
    opd_appointments_count: int
    ipd_active_admissions: int
    lab_tests_performed: int
    bed_occupancy_rate_percentage: float

class FinancialSummary(BaseModel):
    total_revenue_npr: float
    paid_revenue_npr: float
    pending_revenue_npr: float
    department_revenue_breakdown: Dict[str, float]

class FEFOExpiryAlertSummary(BaseModel):
    expired_batch_count: int
    near_expiry_batch_count: int # Within 30 days
