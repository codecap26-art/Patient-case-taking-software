from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.db.database import get_db
from app.db.models.user import User, UserRole
from app.db.models.doctor import Doctor
from app.schemas.doctor import DoctorResponse
from app.core.dependencies import get_current_user, require_doctor, require_role
from app.core.exceptions import NotFoundException

router = APIRouter(prefix="/doctors", tags=["Doctors"])


@router.get("/me", response_model=DoctorResponse)
def get_my_doctor_profile(
    doctor_info: tuple[User, Doctor] = Depends(require_doctor),
):
    _, doctor = doctor_info
    return doctor


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
