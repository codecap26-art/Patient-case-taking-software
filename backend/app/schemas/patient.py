from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field


class PatientBase(BaseModel):
    first_name: str
    last_name: str
    date_of_birth: Optional[str] = None
    gender: Optional[str] = None
    blood_group: Optional[str] = None
    phone: str
    email: Optional[str] = None
    address: Optional[str] = None
    emergency_contact: Optional[str] = None
    allergies: Optional[List[str]] = []
    chronic_conditions: Optional[List[str]] = []


class PatientCreate(PatientBase):
    pass


class PatientUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    date_of_birth: Optional[str] = None
    gender: Optional[str] = None
    blood_group: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    emergency_contact: Optional[str] = None
    allergies: Optional[List[str]] = None
    chronic_conditions: Optional[List[str]] = None


class PatientResponse(PatientBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    patient_identifier: str
    created_at: datetime
    updated_at: datetime



class QRTokenResponse(BaseModel):
    qr_payload: str
    patient_id: str
    expires_in_seconds: int


class QRLinkRequest(BaseModel):
    qr_payload: str
    purpose: str = "Consultation & Case Taking"
