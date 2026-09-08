from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import select, desc
from app.db.models.consent import Consent, ConsentStatus
from app.schemas.consent import ConsentRequestCreate
from app.core.exceptions import NotFoundException
from app.utils.timestamps import utc_now
from app.services.audit_service import AuditService


class ConsentService:
    @staticmethod
    def create_request(db: Session, req: ConsentRequestCreate, user_id: str) -> Consent:
        consent = Consent(
            patient_id=req.patient_id,
            provider_name=req.provider_name,
            provider_type=req.provider_type,
            doctor_name=req.doctor_name,
            purpose=req.purpose,
            requested_scope=req.requested_scope,
            valid_until=req.valid_until,
            status=ConsentStatus.PENDING,
            request_date=utc_now(),
        )
        db.add(consent)
        db.commit()
        db.refresh(consent)

        AuditService.log(
            db,
            action="REQUEST_CONSENT",
            resource_type="consent",
            resource_id=consent.id,
            user_id=user_id,
            details={"provider": req.provider_name, "scope": req.requested_scope},
        )
        return consent

    @staticmethod
    def get_by_id(db: Session, consent_id: str) -> Consent:
        consent = db.scalar(select(Consent).where(Consent.id == consent_id))
        if not consent:
            raise NotFoundException("Consent Request", consent_id)
        return consent

    @staticmethod
    def respond(db: Session, consent_id: str, allow: bool, user_id: str) -> Consent:
        consent = ConsentService.get_by_id(db, consent_id)
        consent.status = ConsentStatus.GRANTED if allow else ConsentStatus.DENIED
        consent.response_date = utc_now()
        db.commit()
        db.refresh(consent)

        AuditService.log(
            db,
            action="RESPOND_CONSENT",
            resource_type="consent",
            resource_id=consent.id,
            user_id=user_id,
            details={"status": consent.status.value},
        )
        return consent

    @staticmethod
    def revoke(db: Session, consent_id: str, user_id: str) -> Consent:
        consent = ConsentService.get_by_id(db, consent_id)
        consent.status = ConsentStatus.REVOKED
        consent.revoked_at = utc_now()
        db.commit()
        db.refresh(consent)

        AuditService.log(
            db,
            action="REVOKE_CONSENT",
            resource_type="consent",
            resource_id=consent.id,
            user_id=user_id,
        )
        return consent

    @staticmethod
    def get_all_for_patient(db: Session, patient_id: str) -> List[Consent]:
        return list(
            db.scalars(
                select(Consent)
                .where(Consent.patient_id == patient_id)
                .order_by(desc(Consent.request_date))
            ).all()
        )

    @staticmethod
    def get_pending(db: Session, patient_id: str) -> List[Consent]:
        return list(
            db.scalars(
                select(Consent)
                .where(Consent.patient_id == patient_id, Consent.status == ConsentStatus.PENDING)
                .order_by(desc(Consent.request_date))
            ).all()
        )

    @staticmethod
    def get_active(db: Session, patient_id: str) -> List[Consent]:
        return list(
            db.scalars(
                select(Consent)
                .where(Consent.patient_id == patient_id, Consent.status == ConsentStatus.GRANTED)
                .order_by(desc(Consent.request_date))
            ).all()
        )

    @staticmethod
    def get_history(db: Session, patient_id: str) -> List[Consent]:
        return list(
            db.scalars(
                select(Consent)
                .where(Consent.patient_id == patient_id, Consent.status != ConsentStatus.PENDING)
                .order_by(desc(Consent.request_date))
            ).all()
        )
