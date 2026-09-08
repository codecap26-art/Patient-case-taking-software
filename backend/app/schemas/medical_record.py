from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, ConfigDict


class MedicalRecordBase(BaseModel):
    title: str
    source_type: str = "CURRENT_SYSTEM"
    source_hospital_id: Optional[str] = None
    external_record_id: Optional[str] = None
    record_type: str
    provider: Optional[str] = None
    summary: Optional[str] = None
    diagnosis: Optional[str] = None
    year: Optional[str] = None
    recorded_at: Optional[str] = None
    data: Optional[Dict[str, Any]] = {}


class MedicalRecordCreate(MedicalRecordBase):
    patient_id: str


class MedicalRecordResponse(MedicalRecordBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    patient_id: str
    created_at: datetime

