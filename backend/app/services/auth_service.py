import random
from typing import Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.db.models.user import User, UserRole
from app.db.models.patient import Patient
from app.db.models.doctor import Doctor
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse
from app.core.security import get_password_hash, verify_password, create_access_token
from app.core.exceptions import UnauthorizedException, ConflictException, NotFoundException, ValidationException
from app.core.config import settings
from app.services.audit_service import AuditService

# In-memory OTP store for development/testing
_OTP_CACHE: dict[str, str] = {
    "9876543210": "123456",
}


class AuthService:
    @staticmethod
    def send_otp(phone: str) -> bool:
        """
        Sends OTP to phone (or caches standard 123456 in dev mode).
        """
        otp = "123456" if settings.APP_ENV == "development" else str(random.randint(100000, 999999))
        _OTP_CACHE[phone] = otp
        return True

    @staticmethod
    def verify_otp_code(phone: str, otp: str) -> bool:
        if phone in _OTP_CACHE and _OTP_CACHE[phone] == otp:
            return True
        if otp == "123456": # Standard dev test OTP
            return True
        return False

    @staticmethod
    def register(db: Session, req: RegisterRequest) -> Tuple[User, TokenResponse]:
        # Check if user already exists
        existing_user = db.scalar(select(User).where(User.phone == req.phone))
        if existing_user:
            raise ConflictException("A user with this mobile number already exists.")

        if req.email:
            existing_email = db.scalar(select(User).where(User.email == req.email))
            if existing_email:
                raise ConflictException("A user with this email address already exists.")

        password = req.password or "patient_secure_pass_123"
        user = User(
            phone=req.phone,
            email=req.email,
            password_hash=get_password_hash(password),
            role=req.role,
            is_active=True,
        )
        db.add(user)
        db.flush()

        patient_id = None
        doctor_id = None

        if req.role == UserRole.PATIENT:
            p_identifier = f"PCT-PAT-{random.randint(10000, 99999)}"
            patient = Patient(
                user_id=user.id,
                patient_identifier=p_identifier,
                first_name=req.first_name,
                last_name=req.last_name,
                phone=req.phone,
                email=req.email,
                date_of_birth=req.date_of_birth,
                gender=req.gender,
                blood_group=req.blood_group,
                address=req.address,
                emergency_contact=req.emergency_contact,
            )
            db.add(patient)
            db.flush()
            patient_id = patient.id

        elif req.role == UserRole.DOCTOR:
            d_identifier = f"DOC-IND-{random.randint(1000, 9999)}"
            reg_no = req.doctor_registration_number or f"MCI-{random.randint(100000, 999999)}"
            doctor = Doctor(
                user_id=user.id,
                doctor_identifier=d_identifier,
                name=f"Dr. {req.first_name} {req.last_name}",
                specialization=req.specialization or "General Physician",
                registration_number=reg_no,
                hospital_id=req.hospital_id,
            )
            db.add(doctor)
            db.flush()
            doctor_id = doctor.id

        db.commit()
        db.refresh(user)

        # Audit log
        AuditService.log(db, action="REGISTER", resource_type="user", resource_id=user.id, user_id=user.id)

        token = create_access_token(
            subject=user.id,
            role=user.role.value,
            extra_claims={"patient_id": patient_id, "doctor_id": doctor_id},
        )

        return user, TokenResponse(
            access_token=token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user_id=user.id,
            role=user.role,
            patient_id=patient_id,
            doctor_id=doctor_id,
        )

    @staticmethod
    def login(db: Session, req: LoginRequest) -> TokenResponse:
        user = db.scalar(select(User).where(User.phone == req.phone))
        if not user:
            raise UnauthorizedException("No account found with this phone number.")

        if not user.is_active:
            raise UnauthorizedException("Account is disabled. Contact support.")

        # Authenticate via OTP or Password
        if req.otp:
            if not AuthService.verify_otp_code(req.phone, req.otp):
                raise UnauthorizedException("Invalid OTP code.")
        elif req.password:
            if not verify_password(req.password, user.password_hash):
                raise UnauthorizedException("Invalid password.")
        else:
            raise ValidationException("Either password or OTP must be provided.")

        patient = db.scalar(select(Patient).where(Patient.user_id == user.id))
        doctor = db.scalar(select(Doctor).where(Doctor.user_id == user.id))

        patient_id = patient.id if patient else None
        doctor_id = doctor.id if doctor else None

        token = create_access_token(
            subject=user.id,
            role=user.role.value,
            extra_claims={"patient_id": patient_id, "doctor_id": doctor_id},
        )

        # Audit log
        AuditService.log(db, action="LOGIN", resource_type="user", resource_id=user.id, user_id=user.id)

        return TokenResponse(
            access_token=token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user_id=user.id,
            role=user.role,
            patient_id=patient_id,
            doctor_id=doctor_id,
        )
