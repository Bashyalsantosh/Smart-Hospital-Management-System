from fastapi import APIRouter
from app.api.v1.endpoints import auth, patients

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(patients.router, prefix="/patients", tags=["Patient Management"])
