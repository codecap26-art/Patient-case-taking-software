from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from app.db.models.user import UserRole


class LoginRequest(BaseModel):
    phone: str = Field(..., description="Mobile number")
    password: Optional[str] = Field(None, description="Password for doctor/admin login")
    otp: Optional[str] = Field(None, description="6-digit OTP for patient quick login")


class SendOtpRequest(BaseModel):
    phone: str = Field(..., description="10-digit mobile number")


class VerifyOtpRequest(BaseModel):
    phone: str = Field(..., description="Mobile number")
    otp: str = Field(..., min_length=4, max_length=6, description="OTP code")


class RegisterRequest(BaseModel):
    phone: str = Field(..., description="Mobile number")
    password: Optional[str] = Field(None, description="Password (optional for patients)")
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    role: UserRole = UserRole.PATIENT
    date_of_birth: Optional[str] = None
    gender: Optional[str] = None
    blood_group: Optional[str] = None
    address: Optional[str] = None
    emergency_contact: Optional[str] = None
    # For doctors
    doctor_registration_number: Optional[str] = None
    specialization: Optional[str] = None
    hospital_id: Optional[str] = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user_id: str
    role: UserRole
    patient_id: Optional[str] = None
    doctor_id: Optional[str] = None


class TokenPayload(BaseModel):
    sub: str
    role: str
    exp: int
