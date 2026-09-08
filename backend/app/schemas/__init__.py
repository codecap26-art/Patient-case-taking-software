from app.schemas.common import StatusResponse, ErrorResponse, HealthResponse, PaginatedResponse
from app.schemas.auth import LoginRequest, RegisterRequest, SendOtpRequest, VerifyOtpRequest, TokenResponse, TokenPayload
from app.schemas.user import UserResponse
from app.schemas.patient import PatientCreate, PatientUpdate, PatientResponse, QRTokenResponse, QRLinkRequest
from app.schemas.doctor import DoctorCreate, DoctorResponse
from app.schemas.consultation import ConsultationCreate, ConsultationUpdate, ConsultationResponse, TranscriptUploadRequest
from app.schemas.clinical_case import ClinicalCaseCreate, ClinicalCaseUpdate, ClinicalCaseResponse, ClinicalCaseConfirmRequest
from app.schemas.prescription import PrescriptionCreate, PrescriptionUpdate, PrescriptionResponse, MedicineItem
from app.schemas.document import DocumentResponse, DocumentUploadMetadata
from app.schemas.medical_record import MedicalRecordCreate, MedicalRecordResponse
from app.schemas.consent import ConsentRequestCreate, ConsentRespondRequest, ConsentResponse
from app.schemas.notification import NotificationCreate, NotificationResponse
from app.schemas.doctor_ai import DoctorAIQueryRequest, DoctorAIQueryResponse, AISource
from app.schemas.interoperability import HospitalResponse, ExternalRecordItem, ExternalMedicationItem, ExternalDiagnosisItem

__all__ = [
    "StatusResponse",
    "ErrorResponse",
    "HealthResponse",
    "PaginatedResponse",
    "LoginRequest",
    "RegisterRequest",
    "SendOtpRequest",
    "VerifyOtpRequest",
    "TokenResponse",
    "TokenPayload",
    "UserResponse",
    "PatientCreate",
    "PatientUpdate",
    "PatientResponse",
    "QRTokenResponse",
    "QRLinkRequest",
    "DoctorCreate",
    "DoctorResponse",
    "ConsultationCreate",
    "ConsultationUpdate",
    "ConsultationResponse",
    "TranscriptUploadRequest",
    "ClinicalCaseCreate",
    "ClinicalCaseUpdate",
    "ClinicalCaseResponse",
    "ClinicalCaseConfirmRequest",
    "PrescriptionCreate",
    "PrescriptionUpdate",
    "PrescriptionResponse",
    "MedicineItem",
    "DocumentResponse",
    "DocumentUploadMetadata",
    "MedicalRecordCreate",
    "MedicalRecordResponse",
    "ConsentRequestCreate",
    "ConsentRespondRequest",
    "ConsentResponse",
    "NotificationCreate",
    "NotificationResponse",
    "DoctorAIQueryRequest",
    "DoctorAIQueryResponse",
    "AISource",
    "HospitalResponse",
    "ExternalRecordItem",
    "ExternalMedicationItem",
    "ExternalDiagnosisItem",
]
