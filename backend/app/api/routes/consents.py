from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models.user import User
from app.db.models.patient import Patient
from app.schemas.consent import (
    ConsentRequestCreate,
    ConsentRespondRequest,
    ConsentResponse,
)
from app.schemas.common import StatusResponse
from app.services.consent_service import ConsentService
from app.core.dependencies import get_current_user, check_patient_data_access

router = APIRouter(prefix="/consents", tags=["Consent & Access Control"])


@router.get("/my-consents", response_model=List[ConsentResponse])
def get_my_consents(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()
    if not patient:
        return []
    return ConsentService.get_active(db, patient.id)


@router.post("/requests", response_model=ConsentResponse, status_code=status.HTTP_201_CREATED)
def request_consent(
    req: ConsentRequestCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return ConsentService.create_request(db, req, current_user.id)


@router.get("/requests", response_model=List[ConsentResponse])
def get_pending_consent_requests(
    patient_id: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    target_id = patient_id
    if not target_id:
        patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()
        target_id = patient.id if patient else ""

    check_patient_data_access(target_id, current_user, db, required_scope="manage_consent")
    return ConsentService.get_pending(db, target_id)


@router.get("/active", response_model=List[ConsentResponse])
def get_active_consents(
    patient_id: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    target_id = patient_id
    if not target_id:
        patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()
        target_id = patient.id if patient else ""

    check_patient_data_access(target_id, current_user, db, required_scope="manage_consent")
    return ConsentService.get_active(db, target_id)


@router.get("/history", response_model=List[ConsentResponse])
def get_consent_history(
    patient_id: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    target_id = patient_id
    if not target_id:
        patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()
        target_id = patient.id if patient else ""

    check_patient_data_access(target_id, current_user, db, required_scope="manage_consent")
    return ConsentService.get_history(db, target_id)


@router.post("/requests/{id}/respond", response_model=ConsentResponse)
def respond_to_consent(
    id: str,
    req: ConsentRespondRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    consent = ConsentService.get_by_id(db, id)
    check_patient_data_access(consent.patient_id, current_user, db, required_scope="manage_consent")
    return ConsentService.respond(db, id, req.allow, current_user.id)


@router.post("/active/{id}/revoke", response_model=ConsentResponse)
def revoke_consent(
    id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    consent = ConsentService.get_by_id(db, id)
    check_patient_data_access(consent.patient_id, current_user, db, required_scope="manage_consent")
    return ConsentService.revoke(db, id, current_user.id)
