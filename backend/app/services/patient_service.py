from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import select, func, desc
from app.db.models.patient import Patient
from app.db.models.medical_record import MedicalRecord
from app.db.models.document import Document
from app.db.models.prescription import Prescription
from app.db.models.consultation import Consultation
from app.schemas.patient import PatientUpdate, QRTokenResponse
from app.core.security import generate_signed_qr_token, verify_signed_qr_token
from app.core.exceptions import NotFoundException, ValidationException
from app.utils.pagination import PaginatedParams
from app.services.audit_service import AuditService


class PatientService:
    @staticmethod
    def get_by_id(db: Session, patient_id: str) -> Patient:
        patient = db.scalar(select(Patient).where(Patient.id == patient_id))
        if not patient:
            raise NotFoundException("Patient", patient_id)
        return patient

    @staticmethod
    def get_by_user_id(db: Session, user_id: str) -> Patient:
        patient = db.scalar(select(Patient).where(Patient.user_id == user_id))
        if not patient:
            raise NotFoundException("Patient profile for user", user_id)
        return patient

    @staticmethod
    def update(db: Session, patient_id: str, data: PatientUpdate, user_id: str) -> Patient:
        patient = PatientService.get_by_id(db, patient_id)
        update_dict = data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(patient, key, value)

        db.commit()
        db.refresh(patient)
        AuditService.log(db, action="UPDATE_PATIENT_PROFILE", resource_type="patient", resource_id=patient.id, user_id=user_id)
        return patient

    @staticmethod
    def generate_qr(patient_id: str) -> QRTokenResponse:
        expiry_sec = 300 # 5 minutes
        signed_token = generate_signed_qr_token(patient_id, expiry_seconds=expiry_sec)
        return QRTokenResponse(
            qr_payload=signed_token,
            patient_id=patient_id,
            expires_in_seconds=expiry_sec,
        )

    @staticmethod
    def link_qr(db: Session, qr_payload: str) -> Patient:
        patient_id = verify_signed_qr_token(qr_payload)
        if not patient_id:
            raise ValidationException("Invalid or expired QR identity token.")
        return PatientService.get_by_id(db, patient_id)

    @staticmethod
    def get_medical_history(db: Session, patient_id: str, pagination: PaginatedParams) -> Tuple[List[MedicalRecord], int]:
        total = db.scalar(select(func.count(MedicalRecord.id)).where(MedicalRecord.patient_id == patient_id)) or 0
        records = db.scalars(
            select(MedicalRecord)
            .where(MedicalRecord.patient_id == patient_id)
            .order_by(desc(MedicalRecord.created_at))
            .offset(pagination.offset)
            .limit(pagination.limit)
        ).all()
        return list(records), total

    @staticmethod
    def get_documents(db: Session, patient_id: str, pagination: PaginatedParams) -> Tuple[List[Document], int]:
        total = db.scalar(select(func.count(Document.id)).where(Document.patient_id == patient_id)) or 0
        docs = db.scalars(
            select(Document)
            .where(Document.patient_id == patient_id)
            .order_by(desc(Document.created_at))
            .offset(pagination.offset)
            .limit(pagination.limit)
        ).all()
        return list(docs), total

    @staticmethod
    def get_prescriptions(db: Session, patient_id: str, pagination: PaginatedParams, active_only: bool = False) -> Tuple[List[Prescription], int]:
        query = select(Prescription).where(Prescription.patient_id == patient_id)
        count_query = select(func.count(Prescription.id)).where(Prescription.patient_id == patient_id)
        if active_only:
            query = query.where(Prescription.is_active.is_(True))
            count_query = count_query.where(Prescription.is_active.is_(True))

        total = db.scalar(count_query) or 0
        prescriptions = db.scalars(
            query.order_by(desc(Prescription.created_at))
            .offset(pagination.offset)
            .limit(pagination.limit)
        ).all()
        return list(prescriptions), total

    @staticmethod
    def list_all(db: Session, pagination: PaginatedParams, search: Optional[str] = None) -> Tuple[List[Patient], int]:
        query = select(Patient)
        count_query = select(func.count(Patient.id))
        if search:
            search_filter = (
                Patient.first_name.ilike(f"%{search}%")
                | Patient.last_name.ilike(f"%{search}%")
                | Patient.phone.ilike(f"%{search}%")
                | Patient.patient_identifier.ilike(f"%{search}%")
            )
            query = query.where(search_filter)
            count_query = count_query.where(search_filter)

        total = db.scalar(count_query) or 0
        patients = db.scalars(
            query.order_by(desc(Patient.created_at))
            .offset(pagination.offset)
            .limit(pagination.limit)
        ).all()
        return list(patients), total

    @staticmethod
    def get_consultations(db: Session, patient_id: str, pagination: PaginatedParams) -> Tuple[List[Consultation], int]:
        total = db.scalar(select(func.count(Consultation.id)).where(Consultation.patient_id == patient_id)) or 0
        consultations = db.scalars(
            select(Consultation)
            .where(Consultation.patient_id == patient_id)
            .order_by(desc(Consultation.started_at))
            .offset(pagination.offset)
            .limit(pagination.limit)
        ).all()
        return list(consultations), total

