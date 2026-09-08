from typing import Generator, Optional, Callable
from fastapi import Depends, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.db.database import get_db
from app.db.models.user import User, UserRole
from app.db.models.patient import Patient
from app.db.models.doctor import Doctor
from app.db.models.consent import Consent, ConsentStatus
from app.core.security import decode_access_token
from app.core.exceptions import UnauthorizedException, ForbiddenException, NotFoundException, ConsentRequiredException

security = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    if not credentials or not credentials.credentials:
        raise UnauthorizedException("Authentication token missing")

    token = credentials.credentials
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise UnauthorizedException("Invalid or expired authentication token")

    user_id = payload["sub"]
    user = db.scalar(select(User).where(User.id == user_id))
    if not user:
        raise UnauthorizedException("User no longer exists")

    if not user.is_active:
        raise ForbiddenException("User account is deactivated")

    return user


def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db),
) -> Optional[User]:
    if not credentials or not credentials.credentials:
        return None

    token = credentials.credentials
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        return None

    user_id = payload["sub"]
    user = db.scalar(select(User).where(User.id == user_id))
    return user if user and user.is_active else None


def require_role(*allowed_roles: UserRole) -> Callable:
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise ForbiddenException(f"Action requires one of the following roles: {[r.value for r in allowed_roles]}")
        return current_user

    return role_checker


def require_patient(
    current_user: User = Depends(require_role(UserRole.PATIENT, UserRole.ADMIN)),
    db: Session = Depends(get_db),
) -> tuple[User, Patient]:
    patient = db.scalar(select(Patient).where(Patient.user_id == current_user.id))
    if not patient and current_user.role != UserRole.ADMIN:
        raise NotFoundException("Patient profile for this user")
    return current_user, patient


def require_doctor(
    current_user: User = Depends(require_role(UserRole.DOCTOR, UserRole.ADMIN)),
    db: Session = Depends(get_db),
) -> tuple[User, Doctor]:
    doctor = db.scalar(select(Doctor).where(Doctor.user_id == current_user.id))
    if not doctor and current_user.role != UserRole.ADMIN:
        raise NotFoundException("Doctor profile for this user")
    return current_user, doctor


def require_admin(current_user: User = Depends(require_role(UserRole.ADMIN))) -> User:
    return current_user


def check_patient_data_access(
    patient_id: str,
    current_user: User,
    db: Session,
    required_scope: str = "read",
) -> None:
    """
    Enforces authorization:
    - If user is ADMIN: allowed.
    - If user is PATIENT: allowed only if user owns the patient record.
    - If user is DOCTOR: allowed only if an active, non-expired Consent exists or direct active consultation exists.
    """
    if current_user.role == UserRole.ADMIN:
        return

    if current_user.role == UserRole.PATIENT:
        patient = db.scalar(select(Patient).where(Patient.user_id == current_user.id))
        if not patient or patient.id != patient_id:
            raise ForbiddenException("You are not authorized to view another patient's medical records")
        return

    if current_user.role == UserRole.DOCTOR:
        doctor = db.scalar(select(Doctor).where(Doctor.user_id == current_user.id))
        if not doctor:
            raise ForbiddenException("Doctor profile not found")

        # Check for active consent
        consent = db.scalar(
            select(Consent).where(
                Consent.patient_id == patient_id,
                Consent.status == ConsentStatus.GRANTED,
            )
        )
        if consent:
            return

        # Fallback: check if doctor has an active consultation with this patient
        from app.db.models.consultation import Consultation
        active_consultation = db.scalar(
            select(Consultation).where(
                Consultation.patient_id == patient_id,
                Consultation.doctor_id == doctor.id,
            )
        )
        if active_consultation:
            return

        raise ConsentRequiredException(patient_id=patient_id, scope=required_scope)
