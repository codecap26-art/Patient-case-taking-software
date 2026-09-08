from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class DoctorAIQueryRequest(BaseModel):
    patient_id: Optional[str] = Field(None, description="Target patient ID (snake_case)")
    patientId: Optional[str] = Field(None, description="Target patient ID (camelCase)")
    question: str = Field(..., min_length=2, max_length=2000, description="Clinical question")
    conversation_history: Optional[List[Dict[str, Any]]] = Field(default_factory=list, description="Previous messages in turn")
    conversationHistory: Optional[List[Dict[str, Any]]] = Field(default_factory=list, description="CamelCase previous messages")
    include_documents: bool = True
    include_consultations: bool = True
    include_prescriptions: bool = True

    @property
    def effective_patient_id(self) -> str:
        return self.patient_id or self.patientId or ""

    @property
    def effective_history(self) -> List[Dict[str, Any]]:
        return self.conversation_history or self.conversationHistory or []


class AISource(BaseModel):
    source_type: str = "document"  # document, consultation, prescription, knowledge_chunk
    type: Optional[str] = None
    id: str
    title: str
    date: Optional[str] = None
    snippet: Optional[str] = None


class DoctorAIQueryResponse(BaseModel):
    patient_id: str
    question: str
    answer: str
    clinical_disclaimer: str = (
        "AI Assistant summary is for clinical reference only. "
        "The consulting doctor remains solely responsible for diagnosis, treatment decisions, and prescriptions."
    )
    sources: List[AISource] = []
    risk_flags: List[str] = []
    confidence: float = 0.95
    conversation_id: Optional[str] = None
    generated_at: str


# --- MediKiosk / DoctorAI Conversational History-Taking Schemas ---

class MessageInput(BaseModel):
    message: str


class PatientInfoSchema(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    sex: Optional[str] = None


class ChiefComplaintSchema(BaseModel):
    complaint: Optional[str] = None
    duration: Optional[str] = None
    severity: Optional[str] = None


class HPISchema(BaseModel):
    onset: Optional[str] = None
    duration: Optional[str] = None
    progression: Optional[str] = None
    location: Optional[str] = None
    character: Optional[str] = None
    severity: Optional[str] = None
    aggravating_factors: Optional[str] = None
    relieving_factors: Optional[str] = None
    associated_symptoms: Optional[str] = None
    previous_episodes: Optional[str] = None


class AyushSchema(BaseModel):
    prakriti: Optional[str] = Field(None, description="Ayurvedic body constitution: Vata, Pitta, Kapha or combinations")
    vikriti: Optional[str] = Field(None, description="Current doshic imbalance state")
    ahara: Optional[str] = Field(None, description="Dietary intake habits and digestive fire (Agni)")
    vihara: Optional[str] = Field(None, description="Daily lifestyle regimen (Dinacharya/Ritucharya)")


class ClinicalHistorySchema(BaseModel):
    patient_info: PatientInfoSchema = Field(default_factory=PatientInfoSchema)
    chief_complaint: ChiefComplaintSchema = Field(default_factory=ChiefComplaintSchema)
    hpi: HPISchema = Field(default_factory=HPISchema)
    ayush: AyushSchema = Field(default_factory=AyushSchema)
    past_medical_history: Optional[str] = None
    medications: Optional[str] = None
    allergies: Optional[str] = None
    family_history: Optional[str] = None
    personal_history: Optional[str] = None


class AIResponseSchema(BaseModel):
    intent: str = Field(description="Intent of the patient's message (e.g., 'answer', 'question', 'greeting', 'emergency')")
    section: str = Field(description="The section of the clinical history being addressed (e.g., 'chief_complaint', 'hpi', 'past_medical_history', 'ayush_assessment', 'completed')")
    extracted_data: Dict[str, Any] = Field(description="Structured data extracted from the patient's answer", default_factory=dict)
    missing_fields: List[str] = Field(description="Fields that are still missing from this section", default_factory=list)
    risk_flags: List[str] = Field(description="Any detected emergency or red-flag symptoms", default_factory=list)
    next_question: str = Field(description="The next natural question to ask the patient, taking context into account")
    confidence: float = Field(description="AI confidence score between 0.0 and 1.0", default=0.95)
