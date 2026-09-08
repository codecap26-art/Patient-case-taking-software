from typing import List, Dict, Any, Optional
from app.integrations.hospitals.base import HospitalAdapter


class HospitalBAdapter(HospitalAdapter):
    """
    Mock adapter for Fortis Heart Centre (FHIR/HL7 format).
    """

    @property
    def hospital_code(self) -> str:
        return "HOSP_B_FORTIS"

    @property
    def hospital_name(self) -> str:
        return "Fortis Hospital - Department of Cardiology"

    def authenticate(self) -> bool:
        return True

    def find_patient(self, phone: str, identifier: Optional[str] = None) -> Optional[Dict[str, Any]]:
        return {
            "external_patient_id": "FORTIS-FHIR-4402",
            "name": "Ramesh Kumar",
            "phone": phone,
            "dob": "1984-06-15",
            "gender": "Male",
        }

    def get_patient_records(self, external_patient_id: str) -> List[Dict[str, Any]]:
        return [
            {
                "external_id": "FORTIS-ENC-902",
                "record_type": "Consultation",
                "title": "Cardiology Review & 12-Lead ECG",
                "date": "2025-10-15",
                "provider": "Dr. Arvind Menon, Fortis Heart Centre",
                "data": {
                    "Blood Pressure": "122/80 mmHg",
                    "Pulse Rate": "72 bpm",
                    "ECG Finding": "Normal Sinus Rhythm, No ST Changes",
                    "Echocardiogram": "LVEF 62%, Normal LV systolic function",
                },
            }
        ]

    def get_medications(self, external_patient_id: str) -> List[Dict[str, Any]]:
        return [
            {
                "hospital_name": self.hospital_name,
                "medication_name": "Tab. Telmisartan 40mg",
                "dosage": "40 mg",
                "frequency": "1-0-0 (Morning after food)",
                "prescribed_date": "2025-10-15",
                "status": "active",
            }
        ]

    def get_diagnoses(self, external_patient_id: str) -> List[Dict[str, Any]]:
        return [
            {
                "hospital_name": self.hospital_name,
                "diagnosis": "Primary Essential Hypertension (Well-Controlled)",
                "icd10_code": "I10",
                "diagnosed_date": "2025-10-15",
                "doctor_name": "Dr. Arvind Menon",
            }
        ]

    def get_lab_reports(self, external_patient_id: str) -> List[Dict[str, Any]]:
        return []
