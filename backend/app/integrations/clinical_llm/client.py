from typing import List, Dict, Any


class ClinicalLLMClient:
    """
    Interface for M3 (Clinical Information Extraction Pipeline).
    Converts speaker transcripts into structured clinical cases.
    """

    async def extract_clinical_case(self, transcript: List[Dict[str, Any]]) -> Dict[str, Any]:
        # Placeholder simulation for M3 integration
        return {
            "symptoms": [
                "Sore throat",
                "Dysphagia (pain on swallowing)",
                "Dry cough",
                "Low-grade fever",
            ],
            "complaints": "Sore throat and dry cough for 3 days",
            "duration": "3 Days",
            "medical_history": ["Stage 1 Essential Hypertension"],
            "allergies": ["Penicillin (severe rash)"],
            "medications": ["Tab. Telmisartan 40mg OD"],
            "family_history": "Father had hypertension and diabetes mellitus",
            "examination": {
                "BP": "124/82 mmHg",
                "Pulse": "78 bpm",
                "Temperature": "99.4 °F",
                "Throat": "Pharyngeal congestion without purulent exudates",
            },
            "doctor_notes": "Prescribed symptomatic therapy. Penicillin avoided due to documented severe allergy.",
        }
