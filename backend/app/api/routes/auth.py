from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.db.database import get_db
from app.db.models.user import User
from app.db.models.patient import Patient
from app.db.models.doctor import Doctor
from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    SendOtpRequest,
    VerifyOtpRequest,
    TokenResponse,
)
from app.schemas.common import StatusResponse
from app.services.auth_service import AuthService
from app.core.dependencies import get_current_user
from app.core.exceptions import UnauthorizedException
from app.core.config import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    _, token_resp = AuthService.register(db, req)
    return token_resp


@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    return AuthService.login(db, req)


@router.post("/send-otp", response_model=StatusResponse)
def send_otp(req: SendOtpRequest):
    AuthService.send_otp(req.phone)
    return StatusResponse(message="OTP sent successfully.")


@router.post("/verify-otp", response_model=TokenResponse)
def verify_otp(req: VerifyOtpRequest, db: Session = Depends(get_db)):
    return AuthService.login(db, LoginRequest(phone=req.phone, otp=req.otp))


@router.get("/me")
def get_me(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    patient = db.scalar(select(Patient).where(Patient.user_id == current_user.id))
    doctor = db.scalar(select(Doctor).where(Doctor.user_id == current_user.id))

    return {
        "user_id": current_user.id,
        "phone": current_user.phone,
        "email": current_user.email,
        "role": current_user.role,
        "patient": patient,
        "doctor": doctor,
    }


@router.post("/logout", response_model=StatusResponse)
def logout(current_user: User = Depends(get_current_user)):
    return StatusResponse(message="Logged out successfully.")
