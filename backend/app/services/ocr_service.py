"""
Service module for OCR document extraction.
Exposes the imported SIH_OCR PaddleOCR service.
"""
from app.services.ocr.ocr_service import OCRService

__all__ = ["OCRService"]
