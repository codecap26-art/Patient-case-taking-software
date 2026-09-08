from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class HospitalAdapter(ABC):
    @property
    @abstractmethod
    def hospital_code(self) -> str:
        pass

    @property
    @abstractmethod
    def hospital_name(self) -> str:
        pass

    @abstractmethod
    def authenticate(self) -> bool:
        pass

    @abstractmethod
    def find_patient(self, phone: str, identifier: Optional[str] = None) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    def get_patient_records(self, external_patient_id: str) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def get_medications(self, external_patient_id: str) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def get_diagnoses(self, external_patient_id: str) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def get_lab_reports(self, external_patient_id: str) -> List[Dict[str, Any]]:
        pass
