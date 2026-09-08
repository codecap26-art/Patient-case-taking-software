from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models.user import User
from app.schemas.patient import (
    PatientResponse,
    PatientUpdate,
    QRTokenResponse,
    QRLinkRequest,
)
from app.schemas.medical_record import MedicalRecordResponse
from app.schemas.document import DocumentResponse
from app.schemas.prescription import PrescriptionResponse
from app.schemas.consultation import ConsultationResponse
from app.services.patient_service import PatientService
from app.services.prescription_service import PrescriptionService
from app.core.dependencies import get_current_user, check_patient_data_access
from app.utils.pagination import PaginatedParams, PaginatedResponse

router = APIRouter(prefix="/patients", tags=["Patients"])


@router.get("/", response_model=PaginatedResponse[PatientResponse])
def list_patients(
    search: Optional[str] = Query(None, description="Search by name, phone or identifier"),
    pagination: PaginatedParams = Depends(),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    patients, total = PatientService.list_all(db, pagination, search=search)
    return PaginatedResponse.create(patients, total, pagination.page, pagination.limit)


@router.get("/me", response_model=PatientResponse)
def get_my_patient_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    return PatientService.get_by_user_id(db, current_user.id)


@router.get("/{patient_id}", response_model=PatientResponse)
def get_patient(
    patient_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_patient_data_access(patient_id, current_user, db, required_scope="read_profile")
    return PatientService.get_by_id(db, patient_id)


@router.put("/{patient_id}", response_model=PatientResponse)
def update_patient(
    patient_id: str,
    data: PatientUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_patient_data_access(patient_id, current_user, db, required_scope="edit_profile")
    return PatientService.update(db, patient_id, data, current_user.id)


@router.get("/{patient_id}/history", response_model=PaginatedResponse[MedicalRecordResponse])
def get_patient_history(
    patient_id: str,
    pagination: PaginatedParams = Depends(),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_patient_data_access(patient_id, current_user, db, required_scope="read_history")
    records, total = PatientService.get_medical_history(db, patient_id, pagination)
    return PaginatedResponse.create(records, total, pagination.page, pagination.limit)


@router.get("/{patient_id}/documents", response_model=PaginatedResponse[DocumentResponse])
def get_patient_documents(
    patient_id: str,
    pagination: PaginatedParams = Depends(),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_patient_data_access(patient_id, current_user, db, required_scope="read_documents")
    docs, total = PatientService.get_documents(db, patient_id, pagination)
    return PaginatedResponse.create(docs, total, pagination.page, pagination.limit)


@router.get("/{patient_id}/prescriptions", response_model=PaginatedResponse[PrescriptionResponse])
def get_patient_prescriptions(
    patient_id: str,
    active_only: bool = Query(False, description="Filter only active prescriptions"),
    pagination: PaginatedParams = Depends(),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_patient_data_access(patient_id, current_user, db, required_scope="read_prescriptions")
    prescriptions, total = PatientService.get_prescriptions(db, patient_id, pagination, active_only=active_only)
    resp_items = [PrescriptionService.to_response(db, p) for p in prescriptions]
    return PaginatedResponse.create(resp_items, total, pagination.page, pagination.limit)


@router.get("/{patient_id}/consultations", response_model=PaginatedResponse[ConsultationResponse])
def get_patient_consultations(
    patient_id: str,
    pagination: PaginatedParams = Depends(),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_patient_data_access(patient_id, current_user, db, required_scope="read_consultations")
    consultations, total = PatientService.get_consultations(db, patient_id, pagination)
    return PaginatedResponse.create(consultations, total, pagination.page, pagination.limit)


@router.post("/{patient_id}/qr-token", response_model=QRTokenResponse)
def get_patient_qr_token(
    patient_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_patient_data_access(patient_id, current_user, db, required_scope="generate_qr")
    return PatientService.generate_qr(patient_id)


@router.post("/qr/link", response_model=PatientResponse)
def link_patient_by_qr(
    req: QRLinkRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return PatientService.link_qr(db, req.qr_payload)
