from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.db.models.medical_record import MedicalRecord
from app.schemas.medical_record import MedicalRecordCreate
from app.core.exceptions import NotFoundException
from app.services.audit_service import AuditService


class MedicalRecordService:
    @staticmethod
    def create(db: Session, data: MedicalRecordCreate, user_id: str) -> MedicalRecord:
        record = MedicalRecord(
            patient_id=data.patient_id,
            title=data.title,
            source_type=data.source_type,
            source_hospital_id=data.source_hospital_id,
            external_record_id=data.external_record_id,
            record_type=data.record_type,
            provider=data.provider,
            summary=data.summary,
            diagnosis=data.diagnosis,
            year=data.year,
            recorded_at=data.recorded_at,
            data=data.data or {},
        )
        db.add(record)
        db.commit()
        db.refresh(record)

        AuditService.log(
            db,
            action="CREATE_MEDICAL_RECORD",
            resource_type="medical_record",
            resource_id=record.id,
            user_id=user_id,
        )
        return record

    @staticmethod
    def get_by_id(db: Session, record_id: str) -> MedicalRecord:
        record = db.scalar(select(MedicalRecord).where(MedicalRecord.id == record_id))
        if not record:
            raise NotFoundException("Medical Record", record_id)
        return record
