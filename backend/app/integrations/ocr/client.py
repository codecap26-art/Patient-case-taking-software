import os
import re
from typing import Dict, Any, Optional
import httpx
from app.core.config import settings
from app.services.ocr_service import OCRService
from app.services.extraction_service import MedicalExtractionService


class OCRClient:
    """
    Real Medical Document OCR & Clinical Extraction Client.
    Extracts text using OCRService and structured parameters using MedicalExtractionService.
    Never hallucinates or returns mock clinical data.
    """

    def __init__(self, service_url: Optional[str] = None):
        self.service_url = service_url or getattr(settings, "OCR_SERVICE_URL", "http://localhost:8000/api/ocr/extract")
        self.ocr_service = OCRService()
        self.extraction_service = MedicalExtractionService()

    async def extract_text(self, file_path: str, filename: str = "", mime_type: str = "") -> Dict[str, Any]:
        """
        Extract text and clinical parameters from image or document.
        """
        # 1. First run real OCR pipeline (PyPDF / Groq Vision)
        if os.path.exists(file_path):
            ocr_res = await self.ocr_service.extract_text_from_document(
                file_path=file_path,
                mime_type=mime_type or "application/octet-stream",
                filename=filename or os.path.basename(file_path),
            )
            raw_text = ocr_res.get("raw_text", "")
            if raw_text and raw_text.strip():
                # Extract clinical metrics using Groq LLM
                extract_res = await self.extraction_service.extract_clinical_data(
                    raw_ocr_text=raw_text,
                    title=filename or "Medical Document",
                    document_type="Diagnostic Report",
                )
                return {
                    "text": raw_text,
                    "confidence": 0.98 if ocr_res.get("success") else 0.70,
                    "lines": [{"text": line, "confidence": 0.98} for line in raw_text.split("\n") if line.strip()],
                    "structured_data": extract_res.get("structured_data", {}),
                    "summary": extract_res.get("summary", ""),
                    "page_count": ocr_res.get("page_count", 1),
                }

        # 2. If external PaddleOCR microservice is specified and configured
        if not getattr(settings, "MOCK_EXTERNAL_SERVICES", True):
            try:
                async with httpx.AsyncClient(timeout=15.0) as client:
                    with open(file_path, "rb") as f:
                        resp = await client.post(
                            self.service_url,
                            files={"file": (filename or "document.jpg", f, mime_type or "image/jpeg")},
                        )
                        if resp.status_code == 200:
                            data = resp.json()
                            raw_text = data.get("text", "")
                            structured = self._parse_clinical_metrics(raw_text)
                            return {
                                "text": raw_text,
                                "confidence": data.get("confidence", 0.95),
                                "lines": data.get("lines", []),
                                "structured_data": structured,
                                "summary": self._generate_summary(filename, structured, raw_text),
                            }
            except Exception:
                pass

        return {
            "text": "",
            "confidence": 0.0,
            "lines": [],
            "structured_data": {},
            "summary": f"No text could be extracted from {filename}.",
            "page_count": 0,
        }

    def _parse_clinical_metrics(self, text: str) -> Dict[str, Any]:
        metrics: Dict[str, Any] = {}
        hb = re.search(r"hemoglobin[:\s]+([\d\.]+\s*(?:g/dl)?)", text, re.IGNORECASE)
        if hb:
            metrics["Hemoglobin"] = hb.group(1).strip()

        wbc = re.search(r"(?:wbc|white blood cell)[:\s]+([\d\.,]+\s*(?:/ul|/cumm)?)", text, re.IGNORECASE)
        if wbc:
            metrics["WBC"] = wbc.group(1).strip()

        chol = re.search(r"(?:total cholesterol|cholesterol)[:\s]+([\d\.]+\s*(?:mg/dl)?)", text, re.IGNORECASE)
        if chol:
            metrics["Total Cholesterol"] = chol.group(1).strip()

        glu = re.search(r"(?:fasting glucose|glucose|sugar)[:\s]+([\d\.]+\s*(?:mg/dl)?)", text, re.IGNORECASE)
        if glu:
            metrics["Glucose"] = glu.group(1).strip()

        return metrics

    def _generate_summary(self, filename: str, structured: Dict[str, Any], text: str) -> str:
        if structured:
            kv_pairs = [f"{k}: {v}" for k, v in structured.items() if k not in ("Document Name", "OCR Status")]
            if kv_pairs:
                return f"OCR Extracted ({filename}): " + "; ".join(kv_pairs)
        return text[:200]
