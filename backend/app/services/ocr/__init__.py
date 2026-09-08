from .config import settings
from .utils import (
    OCRManager,
    validate_and_preprocess_image,
    render_pdf_to_images,
    detect_and_smart_zoom,
    format_ocr_results,
    run_fast_ocr,
    run_bilingual_ocr,
)
from .ocr_service import OCRService

__all__ = [
    "settings",
    "OCRManager",
    "OCRService",
    "validate_and_preprocess_image",
    "render_pdf_to_images",
    "detect_and_smart_zoom",
    "format_ocr_results",
    "run_fast_ocr",
    "run_bilingual_ocr",
]
