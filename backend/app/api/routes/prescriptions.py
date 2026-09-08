from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models.user import User
from app.db.models.doctor import Doctor
from app.schemas.prescription import (
    PrescriptionCreate,
    PrescriptionUpdate,
    PrescriptionResponse,
)
from app.services.prescription_service import PrescriptionService
from app.core.dependencies import get_current_user, require_doctor, check_patient_data_access

router = APIRouter(prefix="/prescriptions", tags=["Prescriptions"])


@router.get("/my-prescriptions", response_model=list[PrescriptionResponse])
def get_my_prescriptions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    from app.db.models.patient import Patient
    patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()
    if not patient:
        return []
    prescriptions = PrescriptionService.get_for_patient(db, patient.id)
    return [PrescriptionService.to_response(db, p) for p in prescriptions]


@router.post("", response_model=PrescriptionResponse, status_code=status.HTTP_201_CREATED)
def create_prescription(
    data: PrescriptionCreate,
    doctor_info: tuple[User, Doctor] = Depends(require_doctor),
    db: Session = Depends(get_db),
):
    user, doctor = doctor_info
    p = PrescriptionService.create(db, data, doctor.id, user.id)
    return PrescriptionService.to_response(db, p)


@router.get("/{id}", response_model=PrescriptionResponse)
def get_prescription(
    id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    prescription = PrescriptionService.get_by_id(db, id)
    check_patient_data_access(prescription.patient_id, current_user, db, required_scope="read_prescriptions")
    return PrescriptionService.to_response(db, prescription)


@router.put("/{id}", response_model=PrescriptionResponse)
def update_prescription(
    id: str,
    data: PrescriptionUpdate,
    doctor_info: tuple[User, Doctor] = Depends(require_doctor),
    db: Session = Depends(get_db),
):
    user, _ = doctor_info
    p = PrescriptionService.update(db, id, data, user.id)
    return PrescriptionService.to_response(db, p)


@router.post("/{id}/confirm", response_model=PrescriptionResponse)
def confirm_prescription(
    id: str,
    doctor_info: tuple[User, Doctor] = Depends(require_doctor),
    db: Session = Depends(get_db),
):
    user, _ = doctor_info
    p = PrescriptionService.confirm(db, id, user.id)
    return PrescriptionService.to_response(db, p)
