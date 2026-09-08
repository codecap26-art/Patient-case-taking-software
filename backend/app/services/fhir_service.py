from typing import Dict, Any, List
from app.db.models.patient import Patient
from app.db.models.consultation import Consultation
from app.db.models.prescription import Prescription
from app.db.models.medical_record import MedicalRecord


class FHIRService:
    """
    Standard FHIR R4 resource conversion layer.
    Keeps FHIR conversion isolated from SQLAlchemy database models.
    """

    @staticmethod
    def patient_to_fhir_patient(patient: Patient) -> Dict[str, Any]:
        return {
            "resourceType": "Patient",
            "id": patient.id,
            "identifier": [
                {
                    "system": "http://patientcasetaking.health/patient-ids",
                    "value": patient.patient_identifier,
                }
            ],
            "name": [
                {
                    "use": "official",
                    "family": patient.last_name,
                    "given": [patient.first_name],
                }
            ],
            "telecom": [
                {"system": "phone", "value": patient.phone, "use": "mobile"},
                *(
                    [{"system": "email", "value": patient.email, "use": "home"}]
                    if patient.email
                    else []
                ),
            ],
            "gender": (patient.gender or "unknown").lower(),
            "birthDate": patient.date_of_birth,
            "address": [{"text": patient.address}] if patient.address else [],
        }

    @staticmethod
    def consultation_to_fhir_encounter(
        consultation: Consultation,
        patient_identifier: str,
        doctor_name: str,
    ) -> Dict[str, Any]:
        return {
            "resourceType": "Encounter",
            "id": consultation.id,
            "status": "finished" if consultation.status.value == "COMPLETED" else "in-progress",
            "class": {
                "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
                "code": "AMB",
                "display": "ambulatory",
            },
            "subject": {
                "reference": f"Patient/{consultation.patient_id}",
                "display": patient_identifier,
            },
            "participant": [
                {
                    "individual": {
                        "reference": f"Practitioner/{consultation.doctor_id}",
                        "display": doctor_name,
                    }
                }
            ],
            "period": {
                "start": consultation.started_at.isoformat(),
                "end": consultation.ended_at.isoformat() if consultation.ended_at else None,
            },
        }

    @staticmethod
    def prescription_to_fhir_medication_requests(
        prescription: Prescription,
        patient_identifier: str,
        doctor_name: str,
    ) -> List[Dict[str, Any]]:
        requests = []
        for idx, med in enumerate(prescription.medicines or []):
            requests.append(
                {
                    "resourceType": "MedicationRequest",
                    "id": f"{prescription.id}-med-{idx}",
                    "status": "active" if prescription.is_active else "completed",
                    "intent": "order",
                    "medicationCodeableConcept": {
                        "text": med.get("name", "Unknown Medication"),
                    },
                    "subject": {
                        "reference": f"Patient/{prescription.patient_id}",
                        "display": patient_identifier,
                    },
                    "requester": {
                        "reference": f"Practitioner/{prescription.doctor_id}",
                        "display": doctor_name,
                    },
                    "dosageInstruction": [
                        {
                            "text": f"{med.get('dosage', '')} - {med.get('frequency', '')} ({med.get('duration', '')})",
                            "additionalInstruction": [
                                {"text": med.get("instructions", "") or med.get("timing", "")}
                            ],
                        }
                    ],
                }
            )
        return requests
