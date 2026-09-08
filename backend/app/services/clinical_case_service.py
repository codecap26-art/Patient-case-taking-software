from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.db.models.clinical_case import ClinicalCase, ClinicalCaseStatus
from app.schemas.clinical_case import ClinicalCaseCreate, ClinicalCaseUpdate, ClinicalCaseConfirmRequest
from app.core.exceptions import NotFoundException, ConflictException
from app.utils.timestamps import utc_now
from app.services.audit_service import AuditService


class ClinicalCaseService:
    @staticmethod
    def create(db: Session, data: ClinicalCaseCreate, user_id: str) -> ClinicalCase:
        # Verify if one already exists for this consultation
        existing = db.scalar(select(ClinicalCase).where(ClinicalCase.consultation_id == data.consultation_id))
        if existing:
            raise ConflictException("A clinical case already exists for this consultation.")

        clinical_case = ClinicalCase(
            consultation_id=data.consultation_id,
            patient_id=data.patient_id,
            symptoms=data.symptoms or [],
            complaints=data.complaints,
            duration=data.duration,
            medical_history=data.medical_history or [],
            allergies=data.allergies or [],
            medications=data.medications or [],
            family_history=data.family_history,
            examination=data.examination or {},
            extracted_data=data.extracted_data or {},
            doctor_notes=data.doctor_notes,
            status=data.status,
        )
        db.add(clinical_case)
        db.commit()
        db.refresh(clinical_case)

        AuditService.log(
            db,
            action="CREATE_CLINICAL_CASE",
            resource_type="clinical_case",
            resource_id=clinical_case.id,
            user_id=user_id,
        )
        return clinical_case

    @staticmethod
    def get_by_id(db: Session, case_id: str) -> ClinicalCase:
        clinical_case = db.scalar(select(ClinicalCase).where(ClinicalCase.id == case_id))
        if not clinical_case:
            raise NotFoundException("Clinical Case", case_id)
        return clinical_case

    @staticmethod
    def get_by_consultation_id(db: Session, consultation_id: str) -> Optional[ClinicalCase]:
        return db.scalar(select(ClinicalCase).where(ClinicalCase.consultation_id == consultation_id))

    @staticmethod
    def update(db: Session, case_id: str, data: ClinicalCaseUpdate, user_id: str) -> ClinicalCase:
        clinical_case = ClinicalCaseService.get_by_id(db, case_id)
        update_dict = data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(clinical_case, key, value)

        db.commit()
        db.refresh(clinical_case)
        AuditService.log(
            db,
            action="UPDATE_CLINICAL_CASE",
            resource_type="clinical_case",
            resource_id=clinical_case.id,
            user_id=user_id,
        )
        return clinical_case

    @staticmethod
    def confirm(
        db: Session,
        case_id: str,
        doctor_id: str,
        req: ClinicalCaseConfirmRequest,
        user_id: str,
    ) -> ClinicalCase:
        """
        The doctor reviews, optionally edits notes, and explicitly confirms the clinical case.
        """
        clinical_case = ClinicalCaseService.get_by_id(db, case_id)
        if req.doctor_notes:
            clinical_case.doctor_notes = req.doctor_notes

        clinical_case.status = ClinicalCaseStatus.CONFIRMED
        clinical_case.confirmed_by_doctor_id = doctor_id
        clinical_case.confirmed_at = utc_now()

        db.commit()
        db.refresh(clinical_case)

        AuditService.log(
            db,
            action="CONFIRM_CLINICAL_CASE",
            resource_type="clinical_case",
            resource_id=clinical_case.id,
            user_id=user_id,
            details={"doctor_id": doctor_id},
        )
        return clinical_case
