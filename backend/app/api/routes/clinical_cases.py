from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models.user import User
from app.db.models.doctor import Doctor
from app.schemas.clinical_case import (
    ClinicalCaseCreate,
    ClinicalCaseUpdate,
    ClinicalCaseResponse,
    ClinicalCaseConfirmRequest,
)
from app.services.clinical_case_service import ClinicalCaseService
from app.core.dependencies import get_current_user, require_doctor

router = APIRouter(prefix="/clinical-cases", tags=["Clinical Cases"])


@router.post("", response_model=ClinicalCaseResponse, status_code=status.HTTP_201_CREATED)
def create_clinical_case(
    data: ClinicalCaseCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return ClinicalCaseService.create(db, data, current_user.id)


@router.get("/{id}", response_model=ClinicalCaseResponse)
def get_clinical_case(
    id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return ClinicalCaseService.get_by_id(db, id)


@router.put("/{id}", response_model=ClinicalCaseResponse)
def update_clinical_case(
    id: str,
    data: ClinicalCaseUpdate,
    doctor_info: tuple[User, Doctor] = Depends(require_doctor),
    db: Session = Depends(get_db),
):
    user, _ = doctor_info
    return ClinicalCaseService.update(db, id, data, user.id)


@router.post("/{id}/confirm", response_model=ClinicalCaseResponse)
def confirm_clinical_case(
    id: str,
    req: ClinicalCaseConfirmRequest,
    doctor_info: tuple[User, Doctor] = Depends(require_doctor),
    db: Session = Depends(get_db),
):
    user, doctor = doctor_info
    return ClinicalCaseService.confirm(db, id, doctor.id, req, user.id)
