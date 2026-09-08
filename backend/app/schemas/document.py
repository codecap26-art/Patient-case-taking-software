from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, ConfigDict
from app.db.models.document import DocumentProcessingStatus


class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    patient_id: str
    uploaded_by: Optional[str] = None
    title: str
    document_type: str
    hospital_name: Optional[str] = None
    document_date: Optional[str] = None
    file_name: str
    mime_type: str
    file_size_bytes: int
    file_size_display: str
    storage_key: str
    extracted_summary: Optional[str] = None
    extracted_text: Optional[str] = None # Raw OCR text
    structured_data: Optional[Dict[str, Any]] = {}
    page_count: Optional[int] = 1
    extraction_error: Optional[str] = None
    doctor_reviewed: bool = False
    doctor_notes: Optional[str] = None
    processing_status: DocumentProcessingStatus
    created_at: datetime
    updated_at: datetime
    processed_at: Optional[datetime] = None


class DocumentUploadMetadata(BaseModel):
    title: str
    document_type: str
    hospital_name: Optional[str] = None
    document_date: Optional[str] = None


class DocumentReviewRequest(BaseModel):
    structured_data: Optional[Dict[str, Any]] = None
    doctor_notes: Optional[str] = None
    confirmed: bool = True

