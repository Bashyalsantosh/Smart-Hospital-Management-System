from fastapi import APIRouter
from app.api.v1.endpoints import auth, patients, appointments, emr

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(patients.router, prefix="/patients", tags=["Patient Management"])
api_router.include_router(appointments.router, prefix="/appointments", tags=["Appointments & Queue"])
api_router.include_router(emr.router, prefix="/emr", tags=["EMR & OPD Consultation"])
