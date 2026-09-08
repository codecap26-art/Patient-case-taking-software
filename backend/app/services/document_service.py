import os
import logging
from datetime import datetime, timezone
from typing import Optional, List, Tuple, Dict, Any
from fastapi import UploadFile
from sqlalchemy.orm import Session
from sqlalchemy import select, func, desc

from app.db.models.document import Document, DocumentProcessingStatus
from app.schemas.document import DocumentUploadMetadata, DocumentReviewRequest
from app.core.exceptions import NotFoundException, ValidationException
from app.services.storage_service import StorageService
from app.services.audit_service import AuditService
from app.services.ocr_service import OCRService
from app.services.extraction_service import MedicalExtractionService
from app.utils.pagination import PaginatedParams

logger = logging.getLogger("patient_case_taking_api.documents")


class DocumentService:
    def __init__(
        self,
        storage_service: Optional[StorageService] = None,
        ocr_service: Optional[OCRService] = None,
        extraction_service: Optional[MedicalExtractionService] = None,
    ):
        self.storage_service = storage_service or StorageService()
        self.ocr_service = ocr_service or OCRService()
        self.extraction_service = extraction_service or MedicalExtractionService()

    async def upload_document(
        self,
        db: Session,
        patient_id: str,
        user_id: str,
        meta: DocumentUploadMetadata,
        file: Optional[UploadFile] = None,
    ) -> Document:
        """
        Upload real document, store binary, perform multi-page OCR and strict clinical extraction.
        """
        if file is None:
            raise ValidationException("An actual document file (PDF, JPG, or PNG) is required for upload.")

        # 1. Save original file securely without modifications
        storage_key, filename, file_size, display_size = self.storage_service.save_file(file, subfolder="documents")
        content_type = file.content_type or "application/octet-stream"
        full_file_path = self.storage_service.get_file_path(storage_key)

        # 2. Create initial Document record in PROCESSING state
        doc = Document(
            patient_id=patient_id,
            uploaded_by=user_id,
            title=meta.title,
            document_type=meta.document_type,
            hospital_name=meta.hospital_name,
            document_date=meta.document_date,
            file_name=filename,
            mime_type=content_type,
            file_size_bytes=file_size,
            file_size_display=display_size,
            storage_key=storage_key,
            processing_status=DocumentProcessingStatus.PROCESSING,
            structured_data={},
            page_count=1,
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)

        # 3. Execute Real Document OCR & Medical Extraction
        await self._run_pipeline_on_document(db, doc, full_file_path, content_type, filename)

        AuditService.log(
            db,
            action="UPLOAD_DOCUMENT",
            resource_type="document",
            resource_id=doc.id,
            user_id=user_id,
            details={"file_name": filename, "file_size": display_size, "status": doc.processing_status.value},
        )
        return doc

    async def reprocess_document(self, db: Session, document_id: str) -> Document:
        """
        Retry / re-run OCR and extraction on an existing document.
        """
        doc = self.get_by_id(db, document_id)
        full_file_path = self.storage_service.get_file_path(doc.storage_key)

        if not os.path.exists(full_file_path):
            raise NotFoundException("Physical document file on disk", doc.storage_key)

        doc.processing_status = DocumentProcessingStatus.PROCESSING
        doc.extraction_error = None
        db.commit()

        await self._run_pipeline_on_document(db, doc, full_file_path, doc.mime_type, doc.file_name)
        return doc

    async def _run_pipeline_on_document(
        self,
        db: Session,
        doc: Document,
        full_file_path: str,
        content_type: str,
        filename: str,
    ) -> None:
        """Internal pipeline: Raw OCR -> Structured Medical Extraction -> Database persistence."""
        try:
            # Step A: Real OCR Extraction
            ocr_result = await self.ocr_service.extract_text_from_document(
                file_path=full_file_path,
                mime_type=content_type,
                filename=filename,
            )

            if not ocr_result["success"] or not ocr_result.get("raw_text", "").strip():
                doc.processing_status = DocumentProcessingStatus.FAILED
                doc.extraction_error = ocr_result.get("error") or "No readable text detected in document."
                db.commit()
                return

            raw_text = ocr_result["raw_text"]
            doc.extracted_text = raw_text
            doc.page_count = ocr_result.get("page_count", 1)
            doc.processing_status = DocumentProcessingStatus.OCR_COMPLETED
            db.commit()

            # Step B: Strict Medical Extraction via Gemini / Local Clinical Extraction (Never invent values)
            extract_res = await self.extraction_service.extract_clinical_data(
                raw_ocr_text=raw_text,
                title=doc.title,
                document_type=doc.document_type,
                hospital_name=doc.hospital_name,
                document_date=doc.document_date,
            )

            if extract_res["success"]:
                doc.structured_data = extract_res.get("structured_data", {})
                doc.extracted_summary = extract_res.get("summary")
                doc.processing_status = DocumentProcessingStatus.EXTRACTION_COMPLETED
                doc.processed_at = datetime.now(timezone.utc)
                doc.extraction_error = None
            else:
                doc.processing_status = DocumentProcessingStatus.FAILED
                doc.extraction_error = extract_res.get("error") or "Clinical extraction failed."

            db.commit()

        except Exception as e:
            logger.error("Pipeline failure for document %s: %s", doc.id, e, exc_info=True)
            doc.processing_status = DocumentProcessingStatus.FAILED
            doc.extraction_error = str(e)
            db.commit()

    def review_document(
        self,
        db: Session,
        document_id: str,
        user_id: str,
        review: DocumentReviewRequest,
    ) -> Document:
        """Doctor review, manual adjustments, and clinical verification."""
        doc = self.get_by_id(db, document_id)
        if review.structured_data is not None:
            doc.structured_data = review.structured_data
        if review.doctor_notes is not None:
            doc.doctor_notes = review.doctor_notes
        doc.doctor_reviewed = review.confirmed
        db.commit()
        db.refresh(doc)

        AuditService.log(
            db,
            action="REVIEW_DOCUMENT",
            resource_type="document",
            resource_id=doc.id,
            user_id=user_id,
            details={"doctor_reviewed": doc.doctor_reviewed},
        )
        return doc

    def get_by_id(self, db: Session, document_id: str) -> Document:
        doc = db.scalar(select(Document).where(Document.id == document_id))
        if not doc:
            raise NotFoundException("Document", document_id)
        return doc

    def get_document_file_info(self, db: Session, document_id: str) -> Tuple[str, str, str]:
        """
        Returns (absolute_file_path, original_filename, mime_type) for serving real file.
        """
        doc = self.get_by_id(db, document_id)
        path = self.storage_service.get_file_path(doc.storage_key)
        if not os.path.exists(path):
            raise NotFoundException("Physical document file on disk", doc.storage_key)
        return path, doc.file_name, doc.mime_type

    def get_patient_documents(
        self, db: Session, patient_id: str, pagination: Optional[PaginatedParams] = None
    ) -> Tuple[List[Document], int]:
        query = select(Document).where(Document.patient_id == patient_id).order_by(desc(Document.created_at))
        count_query = select(func.count(Document.id)).where(Document.patient_id == patient_id)
        total = db.scalar(count_query) or 0
        if pagination:
            query = query.offset(pagination.offset).limit(pagination.limit)
        docs = db.scalars(query).all()
        return list(docs), total

    def delete(self, db: Session, document_id: str, user_id: str) -> bool:
        doc = self.get_by_id(db, document_id)
        self.storage_service.delete_file(doc.storage_key)
        db.delete(doc)
        db.commit()

        AuditService.log(
            db,
            action="DELETE_DOCUMENT",
            resource_type="document",
            resource_id=document_id,
            user_id=user_id,
        )
        return True
