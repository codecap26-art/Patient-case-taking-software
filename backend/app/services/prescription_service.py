from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import select, func, desc
from app.db.models.prescription import Prescription, PrescriptionStatus
from app.db.models.doctor import Doctor
from app.db.models.hospital import Hospital
from app.schemas.prescription import PrescriptionCreate, PrescriptionUpdate, PrescriptionResponse
from app.core.exceptions import NotFoundException
from app.utils.pagination import PaginatedParams
from app.services.audit_service import AuditService


class PrescriptionService:
    @staticmethod
    def create(db: Session, data: PrescriptionCreate, doctor_id: str, user_id: str) -> Prescription:
        prescription = Prescription(
            consultation_id=data.consultation_id,
            patient_id=data.patient_id,
            doctor_id=doctor_id,
            diagnosis_notes=data.diagnosis_notes,
            medicines=[m.model_dump() for m in data.medicines],
            general_advice=data.general_advice,
            doctor_notes=data.doctor_notes,
            follow_up_date=data.follow_up_date,
            status=data.status,
            is_active=data.is_active,
        )
        db.add(prescription)
        db.commit()
        db.refresh(prescription)

        AuditService.log(
            db,
            action="CREATE_PRESCRIPTION",
            resource_type="prescription",
            resource_id=prescription.id,
            user_id=user_id,
            details={"patient_id": data.patient_id, "medicine_count": len(data.medicines)},
        )
        return prescription

    @staticmethod
    def get_by_id(db: Session, prescription_id: str) -> Prescription:
        prescription = db.scalar(select(Prescription).where(Prescription.id == prescription_id))
        if not prescription:
            raise NotFoundException("Prescription", prescription_id)
        return prescription

    @staticmethod
    def update(db: Session, prescription_id: str, data: PrescriptionUpdate, user_id: str) -> Prescription:
        prescription = PrescriptionService.get_by_id(db, prescription_id)
        if data.diagnosis_notes is not None:
            prescription.diagnosis_notes = data.diagnosis_notes
        if data.medicines is not None:
            prescription.medicines = [m.model_dump() for m in data.medicines]
        if data.general_advice is not None:
            prescription.general_advice = data.general_advice
        if data.doctor_notes is not None:
            prescription.doctor_notes = data.doctor_notes
        if data.follow_up_date is not None:
            prescription.follow_up_date = data.follow_up_date
        if data.status is not None:
            prescription.status = data.status
        if data.is_active is not None:
            prescription.is_active = data.is_active

        db.commit()
        db.refresh(prescription)
        AuditService.log(
            db,
            action="UPDATE_PRESCRIPTION",
            resource_type="prescription",
            resource_id=prescription.id,
            user_id=user_id,
        )
        return prescription

    @staticmethod
    def confirm(db: Session, prescription_id: str, user_id: str) -> Prescription:
        prescription = PrescriptionService.get_by_id(db, prescription_id)
        prescription.status = PrescriptionStatus.ACTIVE
        prescription.is_active = True
        db.commit()
        db.refresh(prescription)

        AuditService.log(
            db,
            action="CONFIRM_PRESCRIPTION",
            resource_type="prescription",
            resource_id=prescription.id,
            user_id=user_id,
        )
        return prescription

    @staticmethod
    def to_response(db: Session, p: Prescription) -> PrescriptionResponse:
        doctor = db.scalar(select(Doctor).where(Doctor.id == p.doctor_id))
        doctor_name = doctor.name if doctor else None
        doctor_spec = doctor.specialization if doctor else None
        hospital_name = None
        if doctor and doctor.hospital_id:
            hosp = db.scalar(select(Hospital).where(Hospital.id == doctor.hospital_id))
            if hosp:
                hospital_name = hosp.name

        return PrescriptionResponse(
            id=p.id,
            consultation_id=p.consultation_id,
            patient_id=p.patient_id,
            doctor_id=p.doctor_id,
            diagnosis_notes=p.diagnosis_notes,
            medicines=p.medicines or [],
            general_advice=p.general_advice,
            doctor_notes=p.doctor_notes,
            follow_up_date=p.follow_up_date,
            status=p.status,
            is_active=p.is_active,
            doctor_name=doctor_name,
            doctor_specialization=doctor_spec,
            hospital_name=hospital_name,
            created_at=p.created_at,
            updated_at=p.updated_at,
        )
