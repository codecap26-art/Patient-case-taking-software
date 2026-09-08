from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class DoctorBase(BaseModel):
    name: str
    specialization: str
    registration_number: str
    hospital_id: Optional[str] = None


class DoctorCreate(DoctorBase):
    user_id: str


class DoctorResponse(DoctorBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    doctor_identifier: str
    created_at: datetime
    updated_at: datetime

