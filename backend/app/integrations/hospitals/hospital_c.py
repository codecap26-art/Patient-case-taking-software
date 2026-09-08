from typing import List, Dict, Any, Optional
from app.integrations.hospitals.base import HospitalAdapter


class HospitalCAdapter(HospitalAdapter):
    """
    Mock adapter for Ministry of Ayush Integrated Health Portal / Manipal Hospital.
    """

    @property
    def hospital_code(self) -> str:
        return "HOSP_C_AYUSH"

    @property
    def hospital_name(self) -> str:
        return "Manipal Hospital & Ayush Integrative Health Centre"

    def authenticate(self) -> bool:
        return True

    def find_patient(self, phone: str, identifier: Optional[str] = None) -> Optional[Dict[str, Any]]:
        return {
            "external_patient_id": "AYUSH-MANIPAL-7701",
            "name": "Ramesh Kumar",
            "phone": phone,
            "dob": "1984-06-15",
            "gender": "Male",
        }

    def get_patient_records(self, external_patient_id: str) -> List[Dict[str, Any]]:
        return [
            {
                "external_id": "AYUSH-REC-301",
                "record_type": "Consultation",
                "title": "Seasonal Rhinitis & Prakriti Assessment",
                "date": "2025-04-12",
                "provider": "Dr. S. Ranganathan, Ayush OPD",
                "data": {
                    "Prakriti": "Pitta-Vata Predominant",
                    "Chief Complaint": "Allergic sneezing and nasal congestion during dust exposure",
                    "Assessment": "Allergic Rhinitis (Vataja Pratishyaya)",
                },
            }
        ]

    def get_medications(self, external_patient_id: str) -> List[Dict[str, Any]]:
        return [
            {
                "hospital_name": self.hospital_name,
                "medication_name": "Trikatu Churna + Sitopaladi",
                "dosage": "3g",
                "frequency": "Twice daily with lukewarm water & honey",
                "prescribed_date": "2025-04-12",
                "status": "completed",
            }
        ]

    def get_diagnoses(self, external_patient_id: str) -> List[Dict[str, Any]]:
        return [
            {
                "hospital_name": self.hospital_name,
                "diagnosis": "Allergic Rhinitis / Vataja Pratishyaya",
                "icd10_code": "J30.9",
                "diagnosed_date": "2025-04-12",
                "doctor_name": "Dr. S. Ranganathan",
            }
        ]

    def get_lab_reports(self, external_patient_id: str) -> List[Dict[str, Any]]:
        return []
