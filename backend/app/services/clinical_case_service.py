from typing import Optional, List, Any
import uuid
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.db.models.clinical_case import ClinicalCase, ClinicalCaseStatus
from app.db.models.consultation import Consultation, ConsultationStatus
from app.db.models.patient import Patient
from app.db.models.doctor import Doctor
from app.db.models.user import User, UserRole
from app.schemas.clinical_case import ClinicalCaseCreate, ClinicalCaseUpdate, ClinicalCaseConfirmRequest
from app.core.exceptions import NotFoundException, ConflictException
from app.utils.timestamps import utc_now
from app.services.audit_service import AuditService


class ClinicalCaseService:
    @staticmethod
    def create(db: Session, data: ClinicalCaseCreate, user_id: str) -> ClinicalCase:
        # 1. Resolve Patient
        patient = db.scalar(
            select(Patient).where(
                (Patient.id == data.patient_id) |
                (Patient.patient_identifier == data.patient_id)
            )
        )
        if not patient and data.patient_name:
            patient = db.scalar(
                select(Patient).where(
                    (Patient.first_name.ilike(f"%{data.patient_name}%")) |
                    (Patient.last_name.ilike(f"%{data.patient_name}%"))
                )
            )
        if not patient:
            # Check by phone or patient_id match
            patient = db.scalar(
                select(Patient).where(
                    (Patient.phone == data.patient_id) |
                    (Patient.first_name.ilike(f"%{data.patient_id}%"))
                )
            )
        if not patient:
            # Auto-register patient so consultation/case is never rejected
            name_parts = (data.patient_name or data.patient_id).strip().split()
            first_name = name_parts[0] if name_parts else "Patient"
            last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else "User"
            rand_suffix = str(uuid.uuid4().int)[:5]
            phone_num = f"98765{rand_suffix}"
            
            p_user = User(
                email=f"patient_{rand_suffix}@hospital.local",
                phone=phone_num,
                password_hash="auto_generated_for_case",
                role=UserRole.PATIENT,
                is_active=True,
            )
            db.add(p_user)
            db.flush()

            patient_ident = data.patient_id if (data.patient_id and data.patient_id.startswith("PCT-")) else f"PCT-PAT-{rand_suffix}"
            patient = Patient(
                user_id=p_user.id,
                patient_identifier=patient_ident,
                first_name=first_name,
                last_name=last_name,
                phone=phone_num,
                allergies=[],
                chronic_conditions=[],
            )
            db.add(patient)
            db.flush()

        patient_id = patient.id

        # 2. Resolve Doctor & Consultation
        consultation_id = data.consultation_id
        if not consultation_id:
            doctor = db.scalar(select(Doctor).where(Doctor.user_id == user_id))
            if not doctor:
                doctor = db.scalar(select(Doctor))
            doctor_id = doctor.id if doctor else None

            consultation = Consultation(
                patient_id=patient_id,
                doctor_id=doctor_id,
                status=ConsultationStatus.IN_PROGRESS,
                started_at=utc_now(),
            )
            db.add(consultation)
            db.flush()
            consultation_id = consultation.id
        else:
            existing = db.scalar(select(ClinicalCase).where(ClinicalCase.consultation_id == consultation_id))
            if existing:
                raise ConflictException("A clinical case already exists for this consultation.")

        # 3. Format Symptoms
        formatted_symptoms = []
        for s in (data.symptoms or []):
            if isinstance(s, dict):
                formatted_symptoms.append(f"{s.get('name', '')} ({s.get('duration', '')})".strip())
            else:
                formatted_symptoms.append(str(s))

        complaints_text = data.complaints or data.chief_complaint or "Clinical consultation"

        # 4. Create ClinicalCase
        clinical_case = ClinicalCase(
            consultation_id=consultation_id,
            patient_id=patient_id,
            symptoms=formatted_symptoms,
            complaints=complaints_text,
            duration=data.duration,
            medical_history=[str(m) for m in (data.medical_history or [])],
            allergies=[str(a) for a in (data.allergies or [])],
            medications=[str(m) for m in (data.medications or [])],
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
