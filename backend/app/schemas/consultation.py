from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
from app.db.models.consultation import ConsultationStatus


class TranscriptUtterance(BaseModel):
    speaker: str = Field(..., description="'doctor' or 'patient'")
    text: str
    start: Optional[float] = None
    end: Optional[float] = None


class TranscriptUploadRequest(BaseModel):
    language: str = "en"
    transcript: List[TranscriptUtterance]
    audio_storage_key: Optional[str] = None


class ConsultationCreate(BaseModel):
    patient_id: str
    doctor_id: Optional[str] = None # Inferred from auth token if doctor
    status: ConsultationStatus = ConsultationStatus.IN_PROGRESS


class ConsultationUpdate(BaseModel):
    status: Optional[ConsultationStatus] = None
    ended_at: Optional[datetime] = None
    transcript: Optional[List[TranscriptUtterance]] = None


class ConsultationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    patient_id: str
    doctor_id: str
    status: ConsultationStatus
    started_at: datetime
    ended_at: Optional[datetime] = None
    audio_storage_key: Optional[str] = None
    transcript: Optional[List[dict]] = []
    created_at: datetime
    updated_at: datetime

