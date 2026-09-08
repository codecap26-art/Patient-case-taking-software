import os
import time
import logging
import asyncio
from typing import Dict, Any, List, Optional
import cv2
import base64
from app.core.config import settings as app_settings
from .config import settings as ocr_settings
from .utils import (
    OCRManager,
    validate_and_preprocess_image,
    render_pdf_to_images,
    detect_and_smart_zoom,
    run_fast_ocr,
)

logger = logging.getLogger("patient_case_taking_api.ocr")


class OCRService:
    """
    Imported & adapted SIH_OCR PaddleOCR engine for Patient Case Taking Software.
    Provides in-process, high-throughput OCR inference:
    - Multi-page PDFs (rendered to high-DPI images via PyMuPDF with page-by-page OCR)
    - Medical Images (PNG, JPG, JPEG, WEBP)
    - EXIF auto-rotation & adaptive contrast enhancement
    - Document contour detection & smart digital zoom
    - Multi-column 2D layout segmentation
    - Bounding boxes, lines, and per-line confidence scores
    """

    def __init__(self):
        self.default_lang = getattr(ocr_settings, "DEFAULT_LANGUAGE", "bilingual")

    async def extract_text_from_file(
        self,
        file_bytes: bytes,
        filename: str,
        content_type: str = "",
        lang: Optional[str] = None,
        auto_zoom: bool = True,
        omit_logos: bool = True,
    ) -> Dict[str, Any]:
        """
        Primary SIH_OCR extraction interface accepting raw file bytes.
        """
        start_time = time.perf_counter()
        target_lang = lang or self.default_lang

        if not file_bytes:
            return {
                "success": False,
                "text": "",
                "raw_text": "",
                "lines": [],
                "blocks": [],
                "confidence": 0.0,
                "page_count": 0,
                "pages": [],
                "error": "Uploaded file is empty (0 bytes).",
            }

        # Determine if file is PDF
        lower_content = (content_type or "").lower()
        lower_filename = (filename or "").lower()
        is_pdf = (
            "pdf" in lower_content
            or lower_filename.endswith(".pdf")
            or file_bytes.startswith(b"%PDF-")
        )

        # -------------------------------------------------------------
        # CASE A: MULTI-PAGE PDF DOCUMENT
        # -------------------------------------------------------------
        if is_pdf:
            try:
                rendered_pages = render_pdf_to_images(file_bytes)
            except ValueError as ve:
                return {
                    "success": False,
                    "text": "",
                    "raw_text": "",
                    "lines": [],
                    "blocks": [],
                    "confidence": 0.0,
                    "page_count": 0,
                    "pages": [],
                    "error": str(ve),
                }
            except Exception as e:
                logger.error(f"PDF rendering failure: {e}", exc_info=True)
                return {
                    "success": False,
                    "text": "",
                    "raw_text": "",
                    "lines": [],
                    "blocks": [],
                    "confidence": 0.0,
                    "page_count": 0,
                    "pages": [],
                    "error": f"PDF document processing failed: {str(e)}",
                }

            pages_data = []
            all_lines = []
            all_blocks = []
            compiled_texts = []
            compiled_raw_texts = []
            total_conf = 0.0

            for p_item in rendered_pages:
                p_num = p_item["page_number"]
                p_np = p_item["np_image"]
                p_orig_b64 = p_item["preview_b64"]
                p_w, p_h = p_item["width"], p_item["height"]

                p_input = p_np
                proc_w, proc_h = p_w, p_h
                p_zoom_meta = {
                    "applied": False,
                    "zoom_factor": 1.0,
                    "crop_box": [0, 0, p_w, p_h],
                    "original_size": [p_w, p_h],
                    "zoomed_size": [p_w, p_h],
                    "detection_method": "none",
                    "noise_trimmed_pct": 0.0,
                }
                p_zoomed_b64 = ""
                p_transform = None

                if auto_zoom:
                    try:
                        z_np, z_meta, z_b64, transform = detect_and_smart_zoom(p_np)
                        p_input = z_np
                        p_zoom_meta = z_meta
                        p_zoomed_b64 = z_b64
                        p_transform = transform
                        proc_w = z_meta["zoomed_size"][0]
                        proc_h = z_meta["zoomed_size"][1]
                    except Exception as z_err:
                        logger.warning(f"Smart zoom on PDF page {p_num} skipped: {z_err}")

                try:
                    p_formatted = await asyncio.to_thread(
                        run_fast_ocr,
                        p_input,
                        lang=target_lang,
                        omit_logos=omit_logos,
                        img_width=proc_w,
                        img_height=proc_h,
                        coord_transform=p_transform,
                    )
                except Exception as ocr_err:
                    logger.error(f"OCR error on PDF page {p_num}: {ocr_err}")
                    p_formatted = {"text": "", "raw_text": "", "lines": [], "blocks": [], "confidence": 0.0}

                p_lines = p_formatted.get("lines", [])
                p_blocks = p_formatted.get("blocks", [])
                page_conf = float(p_formatted.get("confidence", 0.0))
                p_text = str(p_formatted.get("text", ""))
                p_raw_text = str(p_formatted.get("raw_text", p_text))

                for l in p_lines:
                    l["page_number"] = p_num
                for b in p_blocks:
                    b["page_number"] = p_num

                total_conf += page_conf
                pages_data.append({
                    "page_number": p_num,
                    "text": p_text,
                    "raw_text": p_raw_text,
                    "lines": p_lines,
                    "blocks": p_blocks,
                    "confidence": page_conf,
                    "zoom_meta": p_zoom_meta,
                    "zoomed_image": p_zoomed_b64 or p_orig_b64,
                    "page_image": p_orig_b64,
                    "dimensions": [p_w, p_h],
                })

                all_lines.extend(p_lines)
                all_blocks.extend(p_blocks)
                if p_text:
                    compiled_texts.append(f"--- Page {p_num} ---\n{p_text}")
                    compiled_raw_texts.append(f"--- Page {p_num} ---\n{p_raw_text}")

            avg_confidence = round(total_conf / max(1, len(pages_data)), 4)
            full_text = "\n\n".join(compiled_texts)
            full_raw_text = "\n\n".join(compiled_raw_texts)
            elapsed_ms = round((time.perf_counter() - start_time) * 1000, 1)

            return {
                "success": bool(full_text.strip() or full_raw_text.strip()),
                "is_pdf": True,
                "total_pages": len(pages_data),
                "page_count": len(pages_data),
                "pages": pages_data,
                "text": full_text,
                "raw_text": full_raw_text or full_text,
                "lines": all_lines,
                "blocks": all_blocks,
                "confidence": avg_confidence,
                "language": target_lang,
                "meta": {
                    "filename": filename,
                    "is_pdf": True,
                    "total_pages": len(pages_data),
                    "line_count": len(all_lines),
                    "word_count": len(full_text.split()) if full_text else 0,
                    "character_count": len(full_text),
                    "processing_time_ms": elapsed_ms,
                },
                "error": None if (full_text.strip() or full_raw_text.strip()) else "No readable text detected in document.",
            }

        # -------------------------------------------------------------
        # CASE B: SINGLE IMAGE (PNG, JPG, JPEG, WEBP)
        # -------------------------------------------------------------
        try:
            np_image, img_meta = validate_and_preprocess_image(file_bytes, filename)
        except ValueError as ve:
            return {
                "success": False,
                "text": "",
                "raw_text": "",
                "lines": [],
                "blocks": [],
                "confidence": 0.0,
                "page_count": 0,
                "pages": [],
                "error": str(ve),
            }
        except Exception as prep_err:
            logger.error(f"Preprocessing error: {prep_err}", exc_info=True)
            return {
                "success": False,
                "text": "",
                "raw_text": "",
                "lines": [],
                "blocks": [],
                "confidence": 0.0,
                "page_count": 0,
                "pages": [],
                "error": f"Image preprocessing failed: {str(prep_err)}",
            }

        orig_w = int(img_meta.get("processed_width") or np_image.shape[1])
        orig_h = int(img_meta.get("processed_height") or np_image.shape[0])

        zoom_meta = {
            "applied": False,
            "zoom_factor": 1.0,
            "crop_box": [0, 0, orig_w, orig_h],
            "original_size": [orig_w, orig_h],
            "zoomed_size": [orig_w, orig_h],
            "detection_method": "none",
            "noise_trimmed_pct": 0.0,
        }
        zoomed_image_b64 = ""
        coord_transform = None
        input_image = np_image
        proc_w = orig_w
        proc_h = orig_h

        if auto_zoom:
            try:
                zoomed_np, z_meta, z_b64, transform = detect_and_smart_zoom(np_image)
                input_image = zoomed_np
                zoom_meta = z_meta
                zoomed_image_b64 = z_b64
                coord_transform = transform
                proc_w = int(zoom_meta["zoomed_size"][0])
                proc_h = int(zoom_meta["zoomed_size"][1])
            except Exception as z_err:
                logger.warning(f"Smart zoom error: {z_err}. Proceeding with standard image.")

        try:
            formatted_data = await asyncio.to_thread(
                run_fast_ocr,
                input_image,
                lang=target_lang,
                omit_logos=omit_logos,
                img_width=proc_w,
                img_height=proc_h,
                coord_transform=coord_transform,
            )
        except Exception as ocr_err:
            logger.error(f"OCR execution failure: {ocr_err}", exc_info=True)
            return {
                "success": False,
                "text": "",
                "raw_text": "",
                "lines": [],
                "blocks": [],
                "confidence": 0.0,
                "page_count": 1,
                "pages": [],
                "error": f"OCR execution failure: {str(ocr_err)}",
            }

        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 1)

        raw_lines = formatted_data.get("lines", [])
        for l in raw_lines:
            l["page_number"] = 1

        raw_blocks = formatted_data.get("blocks", [])
        for b in raw_blocks:
            b["page_number"] = 1

        # Preview image
        bgr_orig = cv2.cvtColor(np_image, cv2.COLOR_RGB2BGR)
        enc_ok, enc_buf = cv2.imencode(".jpg", bgr_orig, [cv2.IMWRITE_JPEG_QUALITY, 85])
        orig_b64 = f"data:image/jpeg;base64,{base64.b64encode(enc_buf.tobytes()).decode('utf-8')}" if enc_ok else ""

        single_page_data = [{
            "page_number": 1,
            "text": formatted_data.get("text", ""),
            "raw_text": formatted_data.get("raw_text", formatted_data.get("text", "")),
            "lines": raw_lines,
            "blocks": raw_blocks,
            "confidence": formatted_data.get("confidence", 0.0),
            "zoom_meta": zoom_meta,
            "zoomed_image": zoomed_image_b64 or orig_b64,
            "page_image": orig_b64,
            "dimensions": [orig_w, orig_h],
        }]

        text = formatted_data.get("text", "")
        raw_text = formatted_data.get("raw_text", text)

        return {
            "success": bool(text.strip() or raw_text.strip()),
            "is_pdf": False,
            "total_pages": 1,
            "page_count": 1,
            "pages": single_page_data,
            "text": text,
            "raw_text": raw_text,
            "lines": raw_lines,
            "blocks": raw_blocks,
            "confidence": formatted_data.get("confidence", 0.0),
            "language": target_lang,
            "zoom_meta": zoom_meta,
            "zoomed_image": zoomed_image_b64 or orig_b64,
            "page_image": orig_b64,
            "meta": {
                **img_meta,
                "is_pdf": False,
                "total_pages": 1,
                "line_count": len(raw_lines),
                "word_count": len(text.split()) if text else 0,
                "character_count": len(text),
                "processing_time_ms": elapsed_ms,
            },
            "error": None if (text.strip() or raw_text.strip()) else "No readable text detected in document.",
        }

    async def extract_text_from_document(
        self,
        file_path: str,
        mime_type: str = "application/pdf",
        filename: str = "",
    ) -> Dict[str, Any]:
        """
        Adapter method for DocumentService accepting a local disk file path.
        """
        if not os.path.exists(file_path):
            return {
                "success": False,
                "text": "",
                "raw_text": "",
                "lines": [],
                "blocks": [],
                "confidence": 0.0,
                "page_count": 0,
                "pages": [],
                "error": f"File does not exist: {file_path}",
            }

        with open(file_path, "rb") as f:
            file_bytes = f.read()

        fn = filename or os.path.basename(file_path)
        return await self.extract_text_from_file(
            file_bytes=file_bytes,
            filename=fn,
            content_type=mime_type,
        )
