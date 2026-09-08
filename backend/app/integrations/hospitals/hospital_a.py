from typing import List, Dict, Any, Optional
from app.integrations.hospitals.base import HospitalAdapter


class HospitalAAdapter(HospitalAdapter):
    """
    Mock adapter for Apollo Speciality Diagnostics (REST JSON API).
    """

    @property
    def hospital_code(self) -> str:
        return "HOSP_A_APOLLO"

    @property
    def hospital_name(self) -> str:
        return "Apollo Speciality Diagnostics"

    def authenticate(self) -> bool:
        return True

    def find_patient(self, phone: str, identifier: Optional[str] = None) -> Optional[Dict[str, Any]]:
        return {
            "external_patient_id": "APOLLO-PAT-9912",
            "name": "Ramesh Kumar",
            "phone": phone,
            "dob": "1984-06-15",
            "gender": "Male",
        }

    def get_patient_records(self, external_patient_id: str) -> List[Dict[str, Any]]:
        return [
            {
                "external_id": "AP-REC-01",
                "record_type": "Lab Test",
                "title": "Comprehensive Metabolic & Lipid Screening",
                "date": "2026-02-18",
                "provider": "Apollo Speciality Diagnostics, Koramangala",
                "data": {
                    "Total Cholesterol": "210 mg/dL",
                    "Triglycerides": "165 mg/dL",
                    "Fasting Blood Sugar": "98 mg/dL",
                    "HbA1c": "5.6%",
                },
            }
        ]

    def get_medications(self, external_patient_id: str) -> List[Dict[str, Any]]:
        return [
            {
                "hospital_name": self.hospital_name,
                "medication_name": "Tab. Atorvastatin 10mg",
                "dosage": "10 mg",
                "frequency": "Once daily at bedtime",
                "prescribed_date": "2026-02-18",
                "status": "active",
            }
        ]

    def get_diagnoses(self, external_patient_id: str) -> List[Dict[str, Any]]:
        return [
            {
                "hospital_name": self.hospital_name,
                "diagnosis": "Borderline Hypercholesterolemia",
                "icd10_code": "E78.00",
                "diagnosed_date": "2026-02-18",
                "doctor_name": "Dr. Sandeep Rao",
            }
        ]

    def get_lab_reports(self, external_patient_id: str) -> List[Dict[str, Any]]:
        return self.get_patient_records(external_patient_id)
