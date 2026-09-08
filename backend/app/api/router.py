from fastapi import APIRouter
from app.api.routes import (
    health,
    auth,
    users,
    patients,
    doctors,
    consultations,
    clinical_cases,
    prescriptions,
    documents,
    medical_records,
    consents,
    notifications,
    interoperability,
    doctor_ai,
    ocr,
)

api_router = APIRouter()

api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(patients.router)
api_router.include_router(doctors.router)
api_router.include_router(consultations.router)
api_router.include_router(clinical_cases.router)
api_router.include_router(prescriptions.router)
api_router.include_router(documents.router)
api_router.include_router(medical_records.router)
api_router.include_router(consents.router)
api_router.include_router(notifications.router)
api_router.include_router(interoperability.router)
api_router.include_router(doctor_ai.router)
api_router.include_router(ocr.router)
