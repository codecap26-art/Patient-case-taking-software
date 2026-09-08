from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models.user import User
from app.db.models.doctor import Doctor
from app.schemas.consultation import (
    ConsultationCreate,
    ConsultationUpdate,
    ConsultationResponse,
    TranscriptUploadRequest,
)
from app.services.consultation_service import ConsultationService
from app.core.dependencies import get_current_user, require_doctor

router = APIRouter(prefix="/consultations", tags=["Consultations"])


@router.post("", response_model=ConsultationResponse, status_code=status.HTTP_201_CREATED)
def create_consultation(
    data: ConsultationCreate,
    doctor_info: tuple[User, Doctor] = Depends(require_doctor),
    db: Session = Depends(get_db),
):
    user, doctor = doctor_info
    data.doctor_id = doctor.id
    return ConsultationService.create(db, data, user.id)


@router.get("/{id}", response_model=ConsultationResponse)
def get_consultation(
    id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return ConsultationService.get_by_id(db, id)


@router.put("/{id}", response_model=ConsultationResponse)
def update_consultation(
    id: str,
    data: ConsultationUpdate,
    doctor_info: tuple[User, Doctor] = Depends(require_doctor),
    db: Session = Depends(get_db),
):
    user, _ = doctor_info
    return ConsultationService.update(db, id, data, user.id)


@router.post("/{id}/transcript", response_model=ConsultationResponse)
def upload_transcript(
    id: str,
    req: TranscriptUploadRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Interface for M2 (Audio / STT module) to push speaker-aware diarized transcript.
    """
    return ConsultationService.upload_transcript(db, id, req, current_user.id)
