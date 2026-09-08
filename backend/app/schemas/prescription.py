from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from app.db.models.prescription import PrescriptionStatus


class MedicineItem(BaseModel):
    name: str = Field(..., description="Medicine brand / generic name")
    dosage: str = Field(..., description="e.g. 500mg, 10ml, 1 tab")
    frequency: str = Field(..., description="e.g. 1-0-1, Once daily")
    duration: str = Field(..., description="e.g. 5 Days, 1 Month")
    timing: Optional[str] = Field(None, description="e.g. After food, Bedtime")
    instructions: Optional[str] = None


class PrescriptionCreate(BaseModel):
    consultation_id: Optional[str] = None
    patient_id: str
    diagnosis_notes: str
    medicines: List[MedicineItem]
    general_advice: Optional[str] = None
    doctor_notes: Optional[str] = None
    follow_up_date: Optional[str] = None
    status: PrescriptionStatus = PrescriptionStatus.ACTIVE
    is_active: bool = True


class PrescriptionUpdate(BaseModel):
    diagnosis_notes: Optional[str] = None
    medicines: Optional[List[MedicineItem]] = None
    general_advice: Optional[str] = None
    doctor_notes: Optional[str] = None
    follow_up_date: Optional[str] = None
    status: Optional[PrescriptionStatus] = None
    is_active: Optional[bool] = None


class PrescriptionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    consultation_id: Optional[str] = None
    patient_id: str
    doctor_id: str
    diagnosis_notes: str
    medicines: List[dict]
    general_advice: Optional[str] = None
    doctor_notes: Optional[str] = None
    follow_up_date: Optional[str] = None
    status: PrescriptionStatus
    is_active: bool
    doctor_name: Optional[str] = None
    doctor_specialization: Optional[str] = None
    hospital_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime

