from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.db.models.hospital import Hospital
from app.db.models.patient import Patient
from app.integrations.hospitals.base import HospitalAdapter
from app.integrations.hospitals.hospital_a import HospitalAAdapter
from app.integrations.hospitals.hospital_b import HospitalBAdapter
from app.integrations.hospitals.hospital_c import HospitalCAdapter
from app.schemas.interoperability import (
    ExternalRecordItem,
    ExternalMedicationItem,
    ExternalDiagnosisItem,
)
from app.services.audit_service import AuditService


class InteroperabilityService:
    def __init__(self):
        self.adapters: Dict[str, HospitalAdapter] = {
            "HOSP_A_APOLLO": HospitalAAdapter(),
            "HOSP_B_FORTIS": HospitalBAdapter(),
            "HOSP_C_AYUSH": HospitalCAdapter(),
        }

    def list_hospitals(self, db: Session) -> List[Hospital]:
        return list(db.scalars(select(Hospital).where(Hospital.is_active.is_(True))).all())

    def get_external_records_for_patient(
        self,
        db: Session,
        patient: Patient,
        user_id: str,
    ) -> List[ExternalRecordItem]:
        all_records: List[ExternalRecordItem] = []
        for code, adapter in self.adapters.items():
            external_patient = adapter.find_patient(phone=patient.phone)
            if external_patient:
                ext_id = external_patient["external_patient_id"]
                raw_records = adapter.get_patient_records(ext_id)
                for r in raw_records:
                    all_records.append(
                        ExternalRecordItem(
                            external_id=r["external_id"],
                            hospital_name=adapter.hospital_name,
                            record_type=r["record_type"],
                            title=r["title"],
                            date=r["date"],
                            data=r.get("data", {}),
                        )
                    )

        AuditService.log(
            db,
            action="FETCH_EXTERNAL_HOSPITAL_RECORDS",
            resource_type="patient",
            resource_id=patient.id,
            user_id=user_id,
            details={"external_records_count": len(all_records)},
        )
        return all_records

    def get_external_medications(
        self,
        db: Session,
        patient: Patient,
        user_id: str,
    ) -> List[ExternalMedicationItem]:
        meds: List[ExternalMedicationItem] = []
        for code, adapter in self.adapters.items():
            external_patient = adapter.find_patient(phone=patient.phone)
            if external_patient:
                raw_meds = adapter.get_medications(external_patient["external_patient_id"])
                for m in raw_meds:
                    meds.append(
                        ExternalMedicationItem(
                            hospital_name=m["hospital_name"],
                            medication_name=m["medication_name"],
                            dosage=m["dosage"],
                            frequency=m["frequency"],
                            prescribed_date=m["prescribed_date"],
                            status=m.get("status", "active"),
                        )
                    )
        return meds

    def get_external_diagnoses(
        self,
        db: Session,
        patient: Patient,
        user_id: str,
    ) -> List[ExternalDiagnosisItem]:
        diagnoses: List[ExternalDiagnosisItem] = []
        for code, adapter in self.adapters.items():
            external_patient = adapter.find_patient(phone=patient.phone)
            if external_patient:
                raw_diag = adapter.get_diagnoses(external_patient["external_patient_id"])
                for d in raw_diag:
                    diagnoses.append(
                        ExternalDiagnosisItem(
                            hospital_name=d["hospital_name"],
                            diagnosis=d["diagnosis"],
                            icd10_code=d.get("icd10_code"),
                            diagnosed_date=d["diagnosed_date"],
                            doctor_name=d.get("doctor_name"),
                        )
                    )
        return diagnoses
