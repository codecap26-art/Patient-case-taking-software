import logging
from typing import Optional, Dict, Any
from fastapi import APIRouter, File, UploadFile, Query, HTTPException, status, Depends, Form, Body, Request
from app.services.ocr.ocr_service import OCRService
from app.services.ocr.config import settings as ocr_settings

from pydantic import BaseModel
from app.services.extraction_service import MedicalExtractionService

logger = logging.getLogger("patient_case_taking_api.ocr")

router = APIRouter(prefix="/ocr", tags=["OCR Service"])
ocr_service = OCRService()
extraction_service = MedicalExtractionService()


class OrganizeTextPayload(BaseModel):
    ocr_text: str
    title: Optional[str] = "Medical Document"
    document_type: Optional[str] = "Clinical Report"
    hospital_name: Optional[str] = None
    document_date: Optional[str] = None


@router.get("/health")
async def ocr_health():
    """Health check for imported SIH_OCR engine."""
    return {
        "status": "healthy",
        "service": "SIH_OCR PaddleOCR Service",
        "supported_languages": ocr_settings.SUPPORTED_LANGUAGES,
        "default_language": ocr_settings.DEFAULT_LANGUAGE,
        "max_upload_mb": ocr_settings.MAX_FILE_SIZE_BYTES // (1024 * 1024),
    }


@router.get("/languages")
async def ocr_languages():
    """Return supported languages dictionary."""
    return {
        "success": True,
        "languages": ocr_settings.SUPPORTED_LANGUAGES,
        "default": ocr_settings.DEFAULT_LANGUAGE,
    }


@router.post("/extract")
async def extract_ocr(
    file: UploadFile = File(..., description="Document file (PDF, PNG, JPG, JPEG, WEBP)"),
    lang: str = Query(ocr_settings.DEFAULT_LANGUAGE, description="Target language ('bilingual', 'en', 'ta')"),
    omit_logos: bool = Query(True, description="Filter out logos, stamps, emblems and graphical noise"),
    auto_zoom: bool = Query(True, description="Enable automatic document boundary detection and smart zoom"),
    organize_with_llm: bool = Query(True, description="Pass OCR converted text to LLM to organize information"),
):
    """
    Extract readable text, line boundaries, confidence scores, and bounding boxes from an uploaded document,
    and automatically give the converted OCR text to the LLM to organize the information.
    Uses imported SIH_OCR engine with thread-safe model caching, EXIF auto-rotation, and smart zoom.
    """
    if not file or not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No file was uploaded.",
        )

    # Validate file type
    content_type = (file.content_type or "").lower()
    ext = file.filename.split(".")[-1].lower() if "." in file.filename else ""
    valid_exts = ["png", "jpg", "jpeg", "webp", "pdf"]

    if content_type and content_type not in ocr_settings.ALLOWED_MIME_TYPES and ext not in valid_exts:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type '{content_type or ext}'. Supported formats: PNG, JPG, JPEG, WEBP, PDF.",
        )

    # Read uploaded bytes
    try:
        file_bytes = await file.read()
    except Exception as read_err:
        logger.error(f"Error reading upload stream: {read_err}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to read uploaded bytes.",
        )

    if not file_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty (0 bytes).",
        )

    if len(file_bytes) > ocr_settings.MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size ({len(file_bytes) / (1024 * 1024):.1f}MB) exceeds maximum limit of {ocr_settings.MAX_FILE_SIZE_BYTES // (1024 * 1024)} MB.",
        )

    # 1. Perform OCR extraction using imported SIH_OCR engine
    result = await ocr_service.extract_text_from_file(
        file_bytes=file_bytes,
        filename=file.filename,
        content_type=content_type,
        lang=lang,
        auto_zoom=auto_zoom,
        omit_logos=omit_logos,
    )

    # 2. Give the OCR converted text to the LLM to organize the information
    if organize_with_llm and result.get("success") and result.get("text"):
        extraction = await extraction_service.extract_clinical_data(
            raw_ocr_text=result["text"],
            title=file.filename,
        )
        result["organized_information"] = extraction.get("organized_information", {})
        result["structured_data"] = extraction.get("structured_data", {})
        result["clinical_summary"] = extraction.get("summary", "")
        result["patient_info"] = extraction.get("patient_info", {})
        result["vital_signs"] = extraction.get("vital_signs", {})
        result["lab_findings"] = extraction.get("lab_findings", [])
        result["medications"] = extraction.get("medications", [])
        result["clinical_problems"] = extraction.get("clinical_problems", [])
        result["allergies"] = extraction.get("allergies", [])
        result["abnormal_findings"] = extraction.get("abnormal_findings", [])

    return result


@router.post("/organize")
async def organize_ocr_text(payload: OrganizeTextPayload):
    """
    Give OCR converted text to the LLM to organize into structured clinical data.
    Accepts JSON payload: { "ocr_text": "...", "title": "...", "document_type": "..." }
    """
    if not payload.ocr_text or not payload.ocr_text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No OCR text provided in 'ocr_text'.",
        )

    # Pass OCR converted text to LLM to organize information
    extraction = await extraction_service.extract_clinical_data(
        raw_ocr_text=payload.ocr_text,
        title=payload.title or "Medical Document",
        document_type=payload.document_type or "Clinical Report",
        hospital_name=payload.hospital_name,
        document_date=payload.document_date,
    )

    return {
        "success": extraction.get("success", False),
        "ocr_text": payload.ocr_text,
        "clinical_summary": extraction.get("summary", ""),
        "organized_information": extraction.get("organized_information", {}),
        "structured_data": extraction.get("structured_data", {}),
        "patient_info": extraction.get("patient_info", {}),
        "vital_signs": extraction.get("vital_signs", {}),
        "lab_findings": extraction.get("lab_findings", []),
        "medications": extraction.get("medications", []),
        "clinical_problems": extraction.get("clinical_problems", []),
        "allergies": extraction.get("allergies", []),
        "abnormal_findings": extraction.get("abnormal_findings", []),
        "error": extraction.get("error"),
    }
