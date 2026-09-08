from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import select, func, desc
from app.db.models.consultation import Consultation, ConsultationStatus
from app.db.models.clinical_case import ClinicalCase, ClinicalCaseStatus
from app.schemas.consultation import ConsultationCreate, ConsultationUpdate, TranscriptUploadRequest
from app.core.exceptions import NotFoundException
from app.utils.pagination import PaginatedParams
from app.utils.timestamps import utc_now
from app.services.audit_service import AuditService


class ConsultationService:
    @staticmethod
    def create(db: Session, data: ConsultationCreate, user_id: str) -> Consultation:
        consultation = Consultation(
            patient_id=data.patient_id,
            doctor_id=data.doctor_id,
            status=data.status,
            started_at=utc_now(),
        )
        db.add(consultation)
        db.commit()
        db.refresh(consultation)

        AuditService.log(
            db,
            action="CREATE_CONSULTATION",
            resource_type="consultation",
            resource_id=consultation.id,
            user_id=user_id,
        )
        return consultation

    @staticmethod
    def get_by_id(db: Session, consultation_id: str) -> Consultation:
        consultation = db.scalar(select(Consultation).where(Consultation.id == consultation_id))
        if not consultation:
            raise NotFoundException("Consultation", consultation_id)
        return consultation

    @staticmethod
    def update(db: Session, consultation_id: str, data: ConsultationUpdate, user_id: str) -> Consultation:
        consultation = ConsultationService.get_by_id(db, consultation_id)
        if data.status is not None:
            consultation.status = data.status
        if data.ended_at is not None:
            consultation.ended_at = data.ended_at
        if data.transcript is not None:
            consultation.transcript = [t.model_dump() for t in data.transcript]

        db.commit()
        db.refresh(consultation)
        AuditService.log(
            db,
            action="UPDATE_CONSULTATION",
            resource_type="consultation",
            resource_id=consultation.id,
            user_id=user_id,
        )
        return consultation

    @staticmethod
    def upload_transcript(
        db: Session,
        consultation_id: str,
        req: TranscriptUploadRequest,
        user_id: str,
    ) -> Consultation:
        """
        Receives speaker-aware transcript from M2 (Audio/STT), stores it in JSONB,
        and creates/updates a draft ClinicalCase for doctor review.
        """
        consultation = ConsultationService.get_by_id(db, consultation_id)
        consultation.transcript = [u.model_dump() for u in req.transcript]
        if req.audio_storage_key:
            consultation.audio_storage_key = req.audio_storage_key
        consultation.status = ConsultationStatus.RECORDED

        # Automatically create or update draft ClinicalCase
        clinical_case = db.scalar(select(ClinicalCase).where(ClinicalCase.consultation_id == consultation_id))
        if not clinical_case:
            # Extract basic text from transcript
            dialogue_text = " ".join([u.text for u in req.transcript])
            clinical_case = ClinicalCase(
                consultation_id=consultation.id,
                patient_id=consultation.patient_id,
                complaints=dialogue_text[:500],
                status=ClinicalCaseStatus.DRAFT,
            )
            db.add(clinical_case)

        db.commit()
        db.refresh(consultation)

        AuditService.log(
            db,
            action="UPLOAD_TRANSCRIPT",
            resource_type="consultation",
            resource_id=consultation.id,
            user_id=user_id,
            details={"transcript_utterance_count": len(req.transcript)},
        )
        return consultation
