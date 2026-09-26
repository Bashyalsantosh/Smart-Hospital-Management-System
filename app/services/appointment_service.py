from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.appointment_repo import AppointmentRepository
from app.schemas.appointment import AppointmentCreate, AppointmentResponse

class AppointmentService:
    def __init__(self, db: AsyncSession):
        self.repo = AppointmentRepository(db)

    async def book_appointment(self, appt_in: AppointmentCreate) -> AppointmentResponse:
        # Token Queue Generation
        token = await self.repo.get_next_token_number(appt_in.doctor_id, appt_in.appointment_date)
        
        # Unique Appt Number: APP-YYYYMMDD-DOCTOR_PREFIX-TOKEN
        date_str = appt_in.appointment_date.strftime("%Y%m%d")
        appt_num = f"APP-{date_str}-{token:03d}"
        
        appointment = await self.repo.create(appt_in, appt_num, token)
        
        # MOCK NOTIFICATION TRIGGER ARCHITECTURE
        # real production integrated with SMS Gateway (e.g. Sparrow SMS / Khalti SMS)
        print(f"[MOCK SMS GATEWAY] Appointment Confirmed for Patient {appt_in.patient_id}. Token No: {token}")
        
        return AppointmentResponse.model_validate(appointment)
