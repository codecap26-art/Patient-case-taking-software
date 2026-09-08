from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models.user import User
from app.schemas.interoperability import (
    HospitalResponse,
    ExternalRecordItem,
    ExternalMedicationItem,
    ExternalDiagnosisItem,
)
from app.services.patient_service import PatientService
from app.services.interoperability_service import InteroperabilityService
from app.core.dependencies import get_current_user, check_patient_data_access

router = APIRouter(prefix="/interoperability", tags=["Interoperability & Hospital FHIR"])
interop_service = InteroperabilityService()


@router.get("/hospitals", response_model=List[HospitalResponse])
def list_connected_hospitals(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return interop_service.list_hospitals(db)


@router.get("/patients/{patient_id}/external-records", response_model=List[ExternalRecordItem])
def get_external_patient_records(
    patient_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_patient_data_access(patient_id, current_user, db, required_scope="read_external_records")
    patient = PatientService.get_by_id(db, patient_id)
    return interop_service.get_external_records_for_patient(db, patient, current_user.id)


@router.get("/patients/{patient_id}/medications", response_model=List[ExternalMedicationItem])
def get_external_medications(
    patient_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_patient_data_access(patient_id, current_user, db, required_scope="read_external_records")
    patient = PatientService.get_by_id(db, patient_id)
    return interop_service.get_external_medications(db, patient, current_user.id)


@router.get("/patients/{patient_id}/diagnoses", response_model=List[ExternalDiagnosisItem])
def get_external_diagnoses(
    patient_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_patient_data_access(patient_id, current_user, db, required_scope="read_external_records")
    patient = PatientService.get_by_id(db, patient_id)
    return interop_service.get_external_diagnoses(db, patient, current_user.id)
