from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.db.models.consent import ConsentStatus


class ConsentRequestCreate(BaseModel):
    patient_id: str
    provider_name: str
    provider_type: Optional[str] = None
    doctor_name: Optional[str] = None
    purpose: str
    requested_scope: str = "Medical History + Previous Prescriptions & Lab Reports"
    valid_until: Optional[str] = "30 Days"


class ConsentRespondRequest(BaseModel):
    allow: bool


class ConsentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    patient_id: str
    provider_name: str
    provider_type: Optional[str] = None
    doctor_name: Optional[str] = None
    purpose: str
    requested_scope: str
    status: ConsentStatus
    request_date: datetime
    response_date: Optional[datetime] = None
    valid_until: Optional[str] = None
    expires_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

