from typing import List, Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from app.db.database import get_db
from app.db.models.user import User, UserRole
from app.db.models.doctor import Doctor
from app.db.models.patient import Patient
from app.db.models.clinical_case import ClinicalCase, ClinicalCaseStatus
from app.db.models.prescription import Prescription
from app.schemas.doctor import DoctorResponse
from app.schemas.patient import PatientResponse
from app.core.dependencies import get_current_user, require_doctor, require_role
from app.core.exceptions import NotFoundException

router = APIRouter(prefix="/doctors", tags=["Doctors"])


@router.get("/me", response_model=DoctorResponse)
def get_my_doctor_profile(
    doctor_info: tuple[User, Doctor] = Depends(require_doctor),
):
    _, doctor = doctor_info
    return doctor


@router.get("/dashboard-stats")
def get_dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    total_patients = db.scalar(select(func.count(Patient.id))) or 0
    today_cases = db.scalar(select(func.count(ClinicalCase.id))) or 0
    pending_reviews = db.scalar(select(func.count(ClinicalCase.id)).where(ClinicalCase.status == ClinicalCaseStatus.DRAFT)) or 0
    total_prescriptions = db.scalar(select(func.count(Prescription.id))) or 0

    return {
        "total_patients": total_patients,
        "today_cases": today_cases,
        "pending_reviews": pending_reviews,
        "total_prescriptions": total_prescriptions,
    }


@router.get("/patients", response_model=List[PatientResponse])
def get_doctor_patients(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    patients = db.scalars(select(Patient).order_by(Patient.created_at.desc())).all()
    return patients



@router.get("/{doctor_id}", response_model=DoctorResponse)
def get_doctor(
    doctor_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    doctor = db.scalar(select(Doctor).where(Doctor.id == doctor_id))
    if not doctor:
        raise NotFoundException("Doctor", doctor_id)
    return doctor
