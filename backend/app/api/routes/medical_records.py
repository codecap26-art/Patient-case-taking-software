from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models.user import User
from app.schemas.medical_record import MedicalRecordCreate, MedicalRecordResponse
from app.services.medical_record_service import MedicalRecordService
from app.core.dependencies import get_current_user, check_patient_data_access

router = APIRouter(prefix="/medical-records", tags=["Medical Records"])


@router.post("", response_model=MedicalRecordResponse, status_code=status.HTTP_201_CREATED)
def create_medical_record(
    data: MedicalRecordCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_patient_data_access(data.patient_id, current_user, db, required_scope="create_records")
    return MedicalRecordService.create(db, data, current_user.id)


@router.get("/my-records", response_model=list[MedicalRecordResponse])
def get_my_medical_records(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    from app.db.models.patient import Patient
    patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()
    if not patient:
        return []
    return MedicalRecordService.get_for_patient(db, patient.id)


@router.get("/{id}", response_model=MedicalRecordResponse)
def get_medical_record(
    id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    record = MedicalRecordService.get_by_id(db, id)
    check_patient_data_access(record.patient_id, current_user, db, required_scope="read_records")
    return record
