from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict


class HospitalResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    code: str
    base_url: str
    integration_type: str
    is_active: bool



class ExternalRecordItem(BaseModel):
    external_id: str
    hospital_name: str
    record_type: str
    title: str
    date: str
    data: Dict[str, Any] = {}
    fhir_resource: Optional[Dict[str, Any]] = None


class ExternalMedicationItem(BaseModel):
    hospital_name: str
    medication_name: str
    dosage: str
    frequency: str
    prescribed_date: str
    status: str = "active"


class ExternalDiagnosisItem(BaseModel):
    hospital_name: str
    diagnosis: str
    icd10_code: Optional[str] = None
    diagnosed_date: str
    doctor_name: Optional[str] = None
