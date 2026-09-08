from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict
from app.db.models.clinical_case import ClinicalCaseStatus


class ClinicalCaseCreate(BaseModel):
    consultation_id: Optional[str] = None
    patient_id: str
    patient_name: Optional[str] = None
    symptoms: Optional[List[Any]] = []
    complaints: Optional[str] = None
    chief_complaint: Optional[str] = None
    duration: Optional[str] = None
    medical_history: Optional[List[Any]] = []
    allergies: Optional[List[Any]] = []
    medications: Optional[List[Any]] = []
    family_history: Optional[str] = None
    examination: Optional[Dict[str, Any]] = {}
    extracted_data: Optional[Dict[str, Any]] = {}
    doctor_notes: Optional[str] = None
    status: ClinicalCaseStatus = ClinicalCaseStatus.DRAFT


class ClinicalCaseUpdate(BaseModel):
    symptoms: Optional[List[str]] = None
    complaints: Optional[str] = None
    duration: Optional[str] = None
    medical_history: Optional[List[str]] = None
    allergies: Optional[List[str]] = None
    medications: Optional[List[str]] = None
    family_history: Optional[str] = None
    examination: Optional[Dict[str, Any]] = None
    doctor_notes: Optional[str] = None
    status: Optional[ClinicalCaseStatus] = None


class ClinicalCaseConfirmRequest(BaseModel):
    doctor_notes: Optional[str] = None


class ClinicalCaseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    consultation_id: str
    patient_id: str
    status: ClinicalCaseStatus
    symptoms: Optional[List[str]] = []
    complaints: Optional[str] = None
    duration: Optional[str] = None
    medical_history: Optional[List[str]] = []
    allergies: Optional[List[str]] = []
    medications: Optional[List[str]] = []
    family_history: Optional[str] = None
    examination: Optional[Dict[str, Any]] = {}
    extracted_data: Optional[Dict[str, Any]] = {}
    doctor_notes: Optional[str] = None
    confirmed_by_doctor_id: Optional[str] = None
    confirmed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

