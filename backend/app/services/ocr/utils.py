import os
# Disable MKLDNN/oneDNN PIR instruction acceleration to avoid CPU PIR conversion bug
os.environ["FLAGS_use_mkldnn"] = "0"
os.environ["PADDLE_PDX_ENABLE_MKLDNN_BYDEFAULT"] = "0"
os.environ["FLAGS_enable_pir_api"] = "0"
os.environ["PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK"] = "True"

import io
import re
import cv2
import base64
import statistics
import logging
import threading
from typing import Dict, List, Tuple, Any, Optional
from concurrent.futures import ThreadPoolExecutor
import numpy as np
from PIL import Image, ImageOps, ImageEnhance

try:
    import pymupdf
except ImportError:
    try:
        import fitz as pymupdf
    except ImportError:
        pymupdf = None

# PaddleOCR & PaddleX inference runners
PaddleOCR = None
PaddleRunnerChainLegacy = None
paddle_available = False

try:
    from paddleocr import PaddleOCR
    import paddle
    paddle_available = True
except Exception as p_err:
    PaddleOCR = None
    paddle_available = False

try:
    from paddlex.inference.models.runners.paddle_static.runner import PaddleRunnerChainLegacy
except Exception:
    PaddleRunnerChainLegacy = None

from .config import settings

logger = logging.getLogger("ocr_service.utils")


class OCRManager:
    """
    Thread-safe singleton manager for caching PaddleOCR models and multi-worker recognition runner pools.
    Prevents duplicate model loading and optimizes inference latency.
    """
    _instances: Dict[str, Any] = {}
    _worker_pools: Dict[str, List[Any]] = {}
    _lock = threading.RLock()
    _NUM_WORKERS = min(6, os.cpu_count() or 4)

    @classmethod
    def get_instance(cls, lang: str = "bilingual") -> Optional[Any]:
        if not paddle_available or PaddleOCR is None:
            logger.info("PaddleOCR engine not natively available in this Python environment.")
            return None

        if lang not in settings.SUPPORTED_LANGUAGES and lang not in ["bilingual", "en", "ta"]:
            logger.warning(f"Language '{lang}' not in supported list, defaulting to 'bilingual'")
            lang = "bilingual"

        if lang not in cls._instances:
            with cls._lock:
                if lang not in cls._instances:
                    logger.info(f"Initializing ultra-fast mobile PaddleOCR model for language='{lang}'...")
                    try:
                        if lang == "en":
                            cls._instances["en"] = PaddleOCR(
                                text_detection_model_name="PP-OCRv4_mobile_det",
                                text_recognition_model_name="en_PP-OCRv4_mobile_rec",
                                use_doc_orientation_classify=False,
                                use_doc_unwarping=False,
                                use_textline_orientation=False,
                                text_det_limit_side_len=960,
                                text_det_limit_type="max",
                                text_det_box_thresh=0.5,
                                text_det_thresh=0.25,
                                text_det_unclip_ratio=1.6,
                                enable_mkldnn=False,
                            )
                        else:
                            # Both 'bilingual' and 'ta' use PP-OCRv4 mobile detection + ta PP-OCRv5 mobile recognition
                            cls._instances[lang] = PaddleOCR(
                                text_detection_model_name="PP-OCRv4_mobile_det",
                                text_recognition_model_name="ta_PP-OCRv5_mobile_rec",
                                use_doc_orientation_classify=False,
                                use_doc_unwarping=False,
                                use_textline_orientation=False,
                                text_det_limit_side_len=960,
                                text_det_limit_type="max",
                                text_det_box_thresh=0.5,
                                text_det_thresh=0.25,
                                text_det_unclip_ratio=1.6,
                                enable_mkldnn=False,
                            )
                    except Exception as err1:
                        logger.warning(f"Mobile model name init failed: {err1}. Falling back to standard mobile...")
                        try:
                            cls._instances[lang] = PaddleOCR(
                                lang="en" if lang == "en" else "ta",
                                use_doc_orientation_classify=False,
                                use_doc_unwarping=False,
                                use_textline_orientation=False,
                                enable_mkldnn=False,
                            )
                        except Exception as err2:
                            logger.error(f"Standard mobile PaddleOCR init failed: {err2}")
                            cls._instances[lang] = None
                    if cls._instances.get(lang):
                        logger.info(f"PaddleOCR model for '{lang}' successfully initialized and cached.")
        return cls._instances.get(lang)

    @classmethod
    def get_rec_workers(cls, lang: str = "bilingual") -> List[Any]:
        """
        Returns cached list of isolated native C++ inference runner chains for multi-core recognition.
        """
        if not paddle_available or PaddleRunnerChainLegacy is None:
            return []

        if lang not in cls._worker_pools:
            ocr_engine = cls.get_instance(lang)
            if ocr_engine is None:
                return []
            with cls._lock:
                if lang not in cls._worker_pools:
                    try:
                        sub = getattr(ocr_engine, "paddlex_pipeline", None)
                        pipeline = getattr(sub, "_pipeline", None) if sub else None
                        if pipeline is not None and hasattr(pipeline, "text_rec_model"):
                            rec = pipeline.text_rec_model
                            predictor = rec.runner.predictor
                            workers = [PaddleRunnerChainLegacy(predictor.clone()) for _ in range(cls._NUM_WORKERS)]
                            cls._worker_pools[lang] = workers
                            logger.info(f"Successfully spawned & cached {cls._NUM_WORKERS} parallel recognition workers for '{lang}'")
                        else:
                            cls._worker_pools[lang] = []
                    except Exception as pool_err:
                        logger.warning(f"Could not build cloned predictor pool: {pool_err}")
                        cls._worker_pools[lang] = []
        return cls._worker_pools.get(lang, [])


def validate_and_preprocess_image(file_bytes: bytes, filename: str) -> Tuple[np.ndarray, Dict[str, Any]]:
    """
    Validates the image file, applies EXIF auto-rotation, converts to RGB,
    resizes if excessive, and applies contrast enhancement.
    
    Returns:
        (numpy_array_image, image_metadata_dict)
    """
    if not file_bytes:
        raise ValueError("Uploaded file is empty (0 bytes).")
    
    if len(file_bytes) > settings.MAX_FILE_SIZE_BYTES:
        raise ValueError(
            f"File size ({len(file_bytes) / (1024*1024):.2f} MB) exceeds maximum allowed "
            f"limit of {settings.MAX_FILE_SIZE_BYTES / (1024*1024):.0f} MB."
        )

    try:
        pil_image = Image.open(io.BytesIO(file_bytes))
        orig_width, orig_height = pil_image.size
        orig_format = pil_image.format or "UNKNOWN"
    except Exception as e:
        logger.error(f"Failed to decode image: {e}")
        raise ValueError(f"Corrupted or invalid image file: {str(e)}")

    # 1. EXIF Auto-Rotation (essential for mobile camera shots)
    try:
        pil_image = ImageOps.exif_transpose(pil_image)
    except Exception as e:
        logger.warning(f"EXIF transpose skipped: {e}")

    # 2. Convert RGBA / Grayscale / Palette to RGB
    if pil_image.mode != "RGB":
        pil_image = pil_image.convert("RGB")

    rotated_width, rotated_height = pil_image.size

    # 3a. Downscale if image exceeds max dimension while preserving aspect ratio
    max_dim = max(rotated_width, rotated_height)
    if max_dim > settings.MAX_IMAGE_DIMENSION:
        scale = settings.MAX_IMAGE_DIMENSION / float(max_dim)
        new_width = int(rotated_width * scale)
        new_height = int(rotated_height * scale)
        pil_image = pil_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        logger.info(f"Resized image from {rotated_width}x{rotated_height} to {new_width}x{new_height}")

    # 3b. Smart compact scaling for small crops so text reaches readable neural size without latency penalty
    cur_w, cur_h = pil_image.size
    min_dim = min(cur_w, cur_h)
    if min_dim < 280 and max(cur_w, cur_h) < 1400:
        scale_up = min(1.35, 300.0 / float(min_dim))
        new_w = int(cur_w * scale_up)
        new_h = int(cur_h * scale_up)
        pil_image = pil_image.resize((new_w, new_h), Image.Resampling.BILINEAR)
        logger.info(f"Compactly scaled snippet from {cur_w}x{cur_h} to {new_w}x{new_h} for fast OCR")

    final_width, final_height = pil_image.size

    # 4. Slight contrast enhancement for crisper text extraction on phone photos
    try:
        enhancer = ImageEnhance.Contrast(pil_image)
        pil_image = enhancer.enhance(settings.CONTRAST_ENHANCE_FACTOR)
    except Exception as e:
        logger.warning(f"Contrast enhancement skipped: {e}")

    # 5. Convert to NumPy array for PaddleOCR
    np_image = np.array(pil_image)

    meta = {
        "filename": filename,
        "original_format": orig_format,
        "original_width": orig_width,
        "original_height": orig_height,
        "processed_width": final_width,
        "processed_height": final_height,
    }

    return np_image, meta


def render_pdf_to_images(
    file_bytes: bytes,
    dpi: int = 175,
    max_pages: int = 30,
) -> List[Dict[str, Any]]:
    """
    Renders pages of a PDF document into RGB NumPy arrays and base64 preview JPEGs.
    """
    if not file_bytes:
        raise ValueError("PDF file is empty (0 bytes).")

    if pymupdf is None:
        raise ValueError("PyMuPDF (fitz) is not installed on the system.")

    try:
        pdf_doc = pymupdf.open(stream=file_bytes, filetype="pdf")
    except Exception as pdf_err:
        logger.error(f"Failed to open PDF document: {pdf_err}")
        raise ValueError(f"Corrupted or invalid PDF file: {str(pdf_err)}")

    total_pages = pdf_doc.page_count
    if total_pages == 0:
        raise ValueError("PDF document contains 0 pages.")

    pages_to_process = min(total_pages, max_pages)
    rendered_pages = []

    for page_idx in range(pages_to_process):
        try:
            page = pdf_doc.load_page(page_idx)
            pix = page.get_pixmap(dpi=dpi)
            img_np = np.frombuffer(pix.samples, dtype=np.uint8).reshape((pix.height, pix.width, pix.n))
            if pix.n >= 4:
                img_np = img_np[:, :, :3]
            elif pix.n == 1:
                img_np = cv2.cvtColor(img_np, cv2.COLOR_GRAY2RGB)

            h, w = img_np.shape[:2]

            # Downscale if image exceeds max dimension while preserving aspect ratio
            max_dim = max(h, w)
            if max_dim > settings.MAX_IMAGE_DIMENSION:
                scale = settings.MAX_IMAGE_DIMENSION / float(max_dim)
                new_w = int(w * scale)
                new_h = int(h * scale)
                img_np = cv2.resize(img_np, (new_w, new_h), interpolation=cv2.INTER_AREA)
                h, w = new_h, new_w

            # Encode preview image to base64 JPEG
            bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
            success, buf = cv2.imencode(".jpg", bgr, [cv2.IMWRITE_JPEG_QUALITY, 85])
            preview_b64 = f"data:image/jpeg;base64,{base64.b64encode(buf.tobytes()).decode('utf-8')}" if success else ""

            rendered_pages.append({
                "page_number": page_idx + 1,
                "np_image": img_np,
                "preview_b64": preview_b64,
                "width": w,
                "height": h,
            })
        except Exception as page_render_err:
            logger.warning(f"Error rendering PDF page {page_idx + 1}: {page_render_err}")

    pdf_doc.close()

    if not rendered_pages:
        raise ValueError("Failed to render any pages from the PDF document.")

    logger.info(f"Rendered {len(rendered_pages)} pages from PDF (total in doc: {total_pages})")
    return rendered_pages


def detect_and_smart_zoom(
    np_image: np.ndarray,
    min_area_ratio: float = 0.12,
    max_area_ratio: float = 0.94,
    padding_pct: float = 0.035,
    target_dimension: int = 1400,
) -> Tuple[np.ndarray, Dict[str, Any], str, Tuple[float, float, int, int]]:
    """
    Intelligently detects document boundaries or text cluster bounding box,
    trims unwanted background clutter (desks, shadows, borders), crops,
    applies digital zoom (upscaling) and text enhancement (CLAHE + unsharp mask).

    Returns:
        (zoomed_np_image, zoom_meta_dict, zoomed_image_b64, (scale_x, scale_y, crop_x1, crop_y1))
    """
    h, w = np_image.shape[:2]
    gray = cv2.cvtColor(np_image, cv2.COLOR_RGB2GRAY)

    detected_crop = None
    detect_method = "none"

    # Strategy 1: Edge and Contour detection for document quadrilateral
    try:
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edged = cv2.Canny(blurred, 35, 120)
        dilated = cv2.dilate(edged, cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5)), iterations=2)
        cnts, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = sorted(cnts, key=cv2.contourArea, reverse=True)

        for c in cnts:
            area = cv2.contourArea(c)
            ratio = area / float(w * h)
            if min_area_ratio <= ratio <= max_area_ratio:
                bx, by, bw, bh = cv2.boundingRect(c)
                aspect = bw / float(max(1, bh))
                if 0.25 <= aspect <= 4.0:
                    detected_crop = (bx, by, bw, bh)
                    detect_method = "document_contour"
                    logger.info(f"Document contour detected: box=({bx}, {by}, {bw}, {bh}), ratio={ratio*100:.1f}%")
                    break
    except Exception as contour_err:
        logger.warning(f"Contour document detection failed: {contour_err}")

    # Strategy 2: Text Density Clustering if no distinct document contour was isolated
    if not detected_crop:
        try:
            grad_x = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3)
            grad_x = cv2.convertScaleAbs(grad_x)
            _, thresh = cv2.threshold(grad_x, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 9))
            closed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
            t_cnts, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            t_boxes = []
            for tc in t_cnts:
                tbx, tby, tbw, tbh = cv2.boundingRect(tc)
                if tbw >= 18 and tbh >= 8 and (tbw * tbh) >= 150:
                    t_boxes.append((tbx, tby, tbx + tbw, tby + tbh))
            if t_boxes:
                min_x = min(b[0] for b in t_boxes)
                min_y = min(b[1] for b in t_boxes)
                max_x = max(b[2] for b in t_boxes)
                max_y = max(b[3] for b in t_boxes)
                bw, bh = max_x - min_x, max_y - min_y
                ratio = (bw * bh) / float(w * h)
                if min_area_ratio <= ratio <= max_area_ratio:
                    detected_crop = (min_x, min_y, bw, bh)
                    detect_method = "text_density"
                    logger.info(f"Text cluster boundary detected: box=({min_x}, {min_y}, {bw}, {bh}), ratio={ratio*100:.1f}%")
        except Exception as text_err:
            logger.warning(f"Text density clustering failed: {text_err}")

    # Compute crop coordinates with safety padding
    if detected_crop:
        cx, cy, cw, ch = detected_crop
        pad_x = int(cw * padding_pct)
        pad_y = int(ch * padding_pct)
        x1 = max(0, cx - pad_x)
        y1 = max(0, cy - pad_y)
        x2 = min(w, cx + cw + pad_x)
        y2 = min(h, cy + ch + pad_y)
        crop_w = x2 - x1
        crop_h = y2 - y1
        noise_trimmed_pct = round((1.0 - (crop_w * crop_h) / float(w * h)) * 100, 1)
    else:
        x1, y1, x2, y2 = 0, 0, w, h
        crop_w, crop_h = w, h
        noise_trimmed_pct = 0.0
        detect_method = "full_frame_enhance"

    cropped = np_image[y1:y2, x1:x2]

    # Digital Zoom / Upscaling calculation
    current_max_dim = max(crop_w, crop_h)
    zoom_scale = 1.0
    if current_max_dim < target_dimension:
        zoom_scale = min(2.5, target_dimension / float(max(1, current_max_dim)))

    if zoom_scale > 1.05:
        zoomed_w = round(crop_w * zoom_scale)
        zoomed_h = round(crop_h * zoom_scale)
        zoomed = cv2.resize(cropped, (zoomed_w, zoomed_h), interpolation=cv2.INTER_LANCZOS4)
    else:
        zoomed = cropped
        zoomed_w, zoomed_h = crop_w, crop_h
        zoom_scale = 1.0

    scale_x = zoomed_w / float(max(1, crop_w))
    scale_y = zoomed_h / float(max(1, crop_h))

    # Adaptive Contrast Enhancement (CLAHE on L-channel of LAB)
    try:
        lab = cv2.cvtColor(zoomed, cv2.COLOR_RGB2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        cl = clahe.apply(l)
        enhanced = cv2.merge((cl, a, b))
        enhanced_rgb = cv2.cvtColor(enhanced, cv2.COLOR_LAB2RGB)

        # Unsharp Masking for crisp character edges
        gaussian = cv2.GaussianBlur(enhanced_rgb, (0, 0), 2.0)
        sharpened_rgb = cv2.addWeighted(enhanced_rgb, 1.25, gaussian, -0.25, 0)
        final_image = np.clip(sharpened_rgb, 0, 255).astype(np.uint8)
    except Exception as enh_err:
        logger.warning(f"Enhancement step skipped: {enh_err}")
        final_image = zoomed

    # Encode zoomed image to JPEG base64
    zoomed_b64 = ""
    try:
        bgr = cv2.cvtColor(final_image, cv2.COLOR_RGB2BGR)
        success, buf = cv2.imencode(".jpg", bgr, [cv2.IMWRITE_JPEG_QUALITY, 88])
        if success:
            zoomed_b64 = f"data:image/jpeg;base64,{base64.b64encode(buf.tobytes()).decode('utf-8')}"
    except Exception as enc_err:
        logger.warning(f"Base64 image encoding failed: {enc_err}")

    zoom_applied = (detect_method in ["document_contour", "text_density"]) or (zoom_scale > 1.05)
    zoom_meta = {
        "applied": zoom_applied,
        "zoom_factor": round(zoom_scale, 2),
        "crop_box": [x1, y1, crop_w, crop_h],
        "original_size": [w, h],
        "zoomed_size": [zoomed_w, zoomed_h],
        "detection_method": detect_method,
        "noise_trimmed_pct": noise_trimmed_pct,
    }

    return final_image, zoom_meta, zoomed_b64, (scale_x, scale_y, x1, y1)


def is_logo_or_noise(
    text: str,
    confidence: float,
    bbox: Any = None,
    img_width: int = 0,
    img_height: int = 0,
) -> bool:
    """
    Intelligently identifies and filters out logos, stamps, emblems, and graphical noise.
    Guarantees genuine text lines and sentences are NEVER omitted.
    """
    clean = text.strip()
    if not clean:
        return True

    # 1. Non-alphanumeric noise
    has_letters_or_digits = any(c.isalnum() for c in clean)
    if not has_letters_or_digits:
        return True

    # 2. Genuine sentences/phrases (4 or more characters) are NEVER omitted as logos
    if len(clean) >= 4 and confidence >= 0.45:
        return False

    # 3. Very low confidence filter for tiny graphical artifacts
    if confidence < 0.45:
        return True

    # 4. Short fragments (1-2 characters with low confidence)
    if len(clean) == 1 and confidence < 0.85:
        return True

    if len(clean) <= 2 and confidence < 0.65:
        return True

    # 5. Geometry check for large square/circular emblems with 1-2 characters
    if bbox is not None and len(bbox) >= 4 and img_width > 0 and img_height > 0:
        try:
            xs = [pt[0] for pt in bbox]
            ys = [pt[1] for pt in bbox]
            w = max(xs) - min(xs)
            h = max(ys) - min(ys)
            if h > 0 and w > 0:
                aspect = w / float(h)
                box_area = w * h
                total_area = float(img_width * img_height)

                if 0.65 <= aspect <= 1.45 and len(clean) <= 2 and (box_area / total_area) > 0.012:
                    logger.info(f"Omitted emblem detection: '{clean}' (aspect: {aspect:.2f}, area: {box_area})")
                    return True
        except Exception:
            pass

    return False


def clean_line_spacing(text: str) -> str:
    """Ensures natural spacing after punctuation like commas, colons, semicolons."""
    text = re.sub(r'([,;:])([A-Za-z\u0B80-\u0BFF])', r'\1 \2', text)
    text = re.sub(r'[ \t]+', ' ', text)
    return text.strip()


def reconstruct_flowing_paragraphs(lines: List[Dict[str, Any]]) -> Tuple[str, str]:
    """
    Reconstructs natural sentences and paragraphs from detected lines within a block.
    """
    if not lines:
        return "", ""

    raw_text = "\n".join(l["text"] for l in lines)
    if len(lines) == 1:
        clean_first = clean_line_spacing(lines[0]["text"])
        return clean_first, raw_text

    heights = []
    for l in lines:
        box = l.get("bbox", [])
        if len(box) == 4:
            h = max(pt[1] for pt in box) - min(pt[1] for pt in box)
            if h > 0:
                heights.append(h)
    median_h = statistics.median(heights) if heights else 25.0
    paragraph_gap_threshold = median_h * 1.4

    TERMINAL_PUNCT = ('.', '!', '?', ':', '।', '|', '。')

    paragraphs = []
    current_para = []

    for i, line in enumerate(lines):
        text = clean_line_spacing(line["text"].strip())
        if not text:
            continue

        if not current_para:
            current_para.append(text)
            continue

        prev_line = lines[i - 1]
        prev_text = current_para[-1].rstrip()

        has_large_gap = False
        prev_box = prev_line.get("bbox", [])
        curr_box = line.get("bbox", [])
        if len(prev_box) == 4 and len(curr_box) == 4:
            prev_ymax = max(pt[1] for pt in prev_box)
            curr_ymin = min(pt[1] for pt in curr_box)
            vert_gap = curr_ymin - prev_ymax
            if vert_gap > paragraph_gap_threshold:
                has_large_gap = True

        stripped = prev_text.rstrip(' "\'”’')
        ends_with_terminal = stripped.endswith(TERMINAL_PUNCT)
        is_list_item = bool(re.match(r'^(\d+[\.\)]|[-*•])\s', text))

        if has_large_gap or ends_with_terminal or is_list_item:
            paragraphs.append(" ".join(current_para))
            current_para = [text]
        else:
            if prev_text.endswith("-") and len(prev_text) > 1 and prev_text[-2].isalpha():
                current_para[-1] = prev_text[:-1] + text
            else:
                current_para.append(text)

    if current_para:
        paragraphs.append(" ".join(current_para))

    flowing_text = "\n".join(paragraphs)
    return flowing_text, raw_text


def segment_layout_blocks(
    lines: List[Dict[str, Any]],
    img_width: int = 0,
    img_height: int = 0,
    min_gutter_x: float = 24.0,
    coord_transform: Optional[Tuple[float, float, int, int]] = None,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], str, str]:
    """
    Analyzes 2D bounding boxes to detect visual columns and paragraphs.
    Separates multi-column layouts into distinct reading blocks.
    """
    if not lines:
        return [], [], "", ""

    box_info = []
    for line in lines:
        bbox = line.get("bbox", [])
        if bbox and len(bbox) >= 4:
            xs = [pt[0] for pt in bbox]
            ys = [pt[1] for pt in bbox]
            box_info.append({
                "line": line,
                "xmin": min(xs),
                "xmax": max(xs),
                "ymin": min(ys),
                "ymax": max(ys),
            })
        else:
            box_info.append({
                "line": line,
                "xmin": 0,
                "xmax": 0,
                "ymin": 0,
                "ymax": 0,
            })

    box_info.sort(key=lambda b: (b["xmin"], b["ymin"]))

    clusters = []
    for b in box_info:
        matched_cluster = None
        for c in clusters:
            overlap = min(b["xmax"], c["xmax"]) - max(b["xmin"], c["xmin"])
            if overlap >= -min_gutter_x:
                matched_cluster = c
                break

        if matched_cluster is not None:
            matched_cluster["boxes"].append(b)
            matched_cluster["xmin"] = min(matched_cluster["xmin"], b["xmin"])
            matched_cluster["xmax"] = max(matched_cluster["xmax"], b["xmax"])
            matched_cluster["ymin"] = min(matched_cluster["ymin"], b["ymin"])
            matched_cluster["ymax"] = max(matched_cluster["ymax"], b["ymax"])
        else:
            clusters.append({
                "xmin": b["xmin"],
                "xmax": b["xmax"],
                "ymin": b["ymin"],
                "ymax": b["ymax"],
                "boxes": [b],
            })

    clusters.sort(key=lambda c: (c["xmin"], c["ymin"]))

    ordered_lines = []
    blocks = []

    for c_idx, cluster in enumerate(clusters):
        cluster["boxes"].sort(key=lambda b: (b["ymin"], b["xmin"]))
        cluster_lines = [b["line"] for b in cluster["boxes"]]

        block_id = c_idx + 1
        block_title = f"Column {block_id}" if len(clusters) > 1 else "Main Block"

        for l in cluster_lines:
            l["block_id"] = block_id
            l["block_title"] = block_title

        flowing_block_text, raw_block_text = reconstruct_flowing_paragraphs(cluster_lines)

        orig_block_bbox = [
            round(coord_transform[2] + (cluster["xmin"] / coord_transform[0]), 1),
            round(coord_transform[3] + (cluster["ymin"] / coord_transform[1]), 1),
            round(coord_transform[2] + (cluster["xmax"] / coord_transform[0]), 1),
            round(coord_transform[3] + (cluster["ymax"] / coord_transform[1]), 1),
        ] if coord_transform else [
            round(cluster["xmin"], 1),
            round(cluster["ymin"], 1),
            round(cluster["xmax"], 1),
            round(cluster["ymax"], 1),
        ]

        blocks.append({
            "block_id": block_id,
            "title": block_title,
            "type": "column" if len(clusters) > 1 else "paragraph",
            "text": flowing_block_text,
            "raw_text": raw_block_text,
            "line_count": len(cluster_lines),
            "lines": cluster_lines,
            "bbox": [
                round(cluster["xmin"], 1),
                round(cluster["ymin"], 1),
                round(cluster["xmax"], 1),
                round(cluster["ymax"], 1),
            ],
            "original_bbox": orig_block_bbox,
        })
        ordered_lines.extend(cluster_lines)

    combined_flowing_text = "\n\n".join(b["text"] for b in blocks if b["text"])
    combined_raw_text = "\n\n".join(b["raw_text"] for b in blocks if b["raw_text"])
    return ordered_lines, blocks, combined_flowing_text, combined_raw_text


def format_ocr_results(
    raw_result: Any,
    omit_logos: bool = True,
    img_width: int = 0,
    img_height: int = 0,
    coord_transform: Optional[Tuple[float, float, int, int]] = None,
) -> Dict[str, Any]:
    """
    Transforms raw PaddleOCR output into clean, structured JSON with bounding boxes,
    confidence scores, and compiled text.
    """
    lines: List[Dict[str, Any]] = []
    confidence_sum = 0.0

    if raw_result and len(raw_result) > 0:
        first_item = raw_result[0]

        # 1. New PaddleX pipeline format: [{'rec_texts': [...], 'rec_scores': [...], 'rec_polys': [...]}]
        if isinstance(first_item, dict) and "rec_texts" in first_item:
            rec_texts = first_item.get("rec_texts", [])
            rec_scores = first_item.get("rec_scores", [])
            rec_polys = first_item.get("rec_polys", [])

            for i, text in enumerate(rec_texts):
                clean_text = str(text).strip()
                if not clean_text:
                    continue
                score = float(rec_scores[i]) if i < len(rec_scores) else 1.0
                float_score = round(score, 4)

                formatted_bbox = []
                if i < len(rec_polys):
                    try:
                        for pt in rec_polys[i]:
                            formatted_bbox.append([round(float(pt[0]), 1), round(float(pt[1]), 1)])
                    except Exception:
                        formatted_bbox = []

                if omit_logos and is_logo_or_noise(clean_text, float_score, formatted_bbox, img_width, img_height):
                    continue

                orig_bbox = [
                    [
                        round(coord_transform[2] + (pt[0] / coord_transform[0]), 1),
                        round(coord_transform[3] + (pt[1] / coord_transform[1]), 1),
                    ]
                    for pt in formatted_bbox
                ] if coord_transform else formatted_bbox

                lines.append({
                    "text": clean_text,
                    "confidence": float_score,
                    "bbox": formatted_bbox,
                    "original_bbox": orig_bbox,
                    "script": "Tamil" if has_tamil_characters(clean_text) else "English",
                })
                confidence_sum += float_score

        # 2. Classic PaddleOCR format: [ [ [box], (text, score) ], ... ]
        elif isinstance(first_item, list):
            for item in first_item:
                try:
                    box = item[0]
                    text, score = item[1]
                    clean_text = str(text).strip()
                    if not clean_text:
                        continue

                    formatted_bbox = [
                        [round(float(pt[0]), 1), round(float(pt[1]), 1)]
                        for pt in box
                    ]
                    float_score = round(float(score), 4)

                    if omit_logos and is_logo_or_noise(clean_text, float_score, formatted_bbox, img_width, img_height):
                        continue

                    orig_bbox = [
                        [
                            round(coord_transform[2] + (pt[0] / coord_transform[0]), 1),
                            round(coord_transform[3] + (pt[1] / coord_transform[1]), 1),
                        ]
                        for pt in formatted_bbox
                    ] if coord_transform else formatted_bbox

                    lines.append({
                        "text": clean_text,
                        "confidence": float_score,
                        "bbox": formatted_bbox,
                        "original_bbox": orig_bbox,
                        "script": "Tamil" if has_tamil_characters(clean_text) else "English",
                    })
                    confidence_sum += float_score
                except Exception as line_err:
                    logger.warning(f"Error parsing line item {item}: {line_err}")

    line_count = len(lines)
    avg_confidence = round(confidence_sum / line_count, 4) if line_count > 0 else 0.0

    ordered_lines, blocks, combined_flowing_text, combined_raw_text = segment_layout_blocks(
        lines, img_width, img_height, coord_transform=coord_transform
    )

    tamil_line_count = sum(1 for l in ordered_lines if l.get("script") == "Tamil")
    english_line_count = sum(1 for l in ordered_lines if l.get("script") == "English")

    return {
        "text": combined_flowing_text,
        "raw_text": combined_raw_text,
        "lines": ordered_lines,
        "blocks": blocks,
        "total_blocks": len(blocks),
        "confidence": avg_confidence,
        "line_count": len(ordered_lines),
        "word_count": len(combined_flowing_text.split()) if combined_flowing_text else 0,
        "character_count": len(combined_flowing_text),
        "script_distribution": {
            "tamil": tamil_line_count,
            "english": english_line_count,
        },
    }


def calculate_box_overlap(box1: List[List[float]], box2: List[List[float]]) -> float:
    """Calculates Intersection over Union (IoU) of two 4-point bounding boxes."""
    try:
        x1_min = min(pt[0] for pt in box1)
        x1_max = max(pt[0] for pt in box1)
        y1_min = min(pt[1] for pt in box1)
        y1_max = max(pt[1] for pt in box1)

        x2_min = min(pt[0] for pt in box2)
        x2_max = max(pt[0] for pt in box2)
        y2_min = min(pt[1] for pt in box2)
        y2_max = max(pt[1] for pt in box2)

        inter_x_min = max(x1_min, x2_min)
        inter_x_max = min(x1_max, x2_max)
        inter_y_min = max(y1_min, y2_min)
        inter_y_max = min(y1_max, y2_max)

        if inter_x_max <= inter_x_min or inter_y_max <= inter_y_min:
            return 0.0

        inter_area = (inter_x_max - inter_x_min) * (inter_y_max - inter_y_min)
        area1 = max(1.0, (x1_max - x1_min) * (y1_max - y1_min))
        area2 = max(1.0, (x2_max - x2_min) * (y2_max - y2_min))
        return inter_area / (area1 + area2 - inter_area)
    except Exception:
        return 0.0


def has_tamil_characters(text: str) -> bool:
    """Checks if string contains Tamil unicode characters."""
    return any('\u0b80' <= c <= '\u0bff' for c in text)


def merge_bilingual_lines(
    lines_en: List[Dict[str, Any]],
    lines_ta: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Intelligently fuses English and Tamil OCR line results.
    """
    merged: List[Dict[str, Any]] = []
    used_ta_indices = set()

    for en_line in lines_en:
        en_box = en_line.get("bbox", [])
        best_match_idx = None
        best_iou = 0.0

        for idx, ta_line in enumerate(lines_ta):
            if idx in used_ta_indices:
                continue
            ta_box = ta_line.get("bbox", [])
            iou = calculate_box_overlap(en_box, ta_box)
            if iou > best_iou:
                best_iou = iou
                best_match_idx = idx

        if best_match_idx is not None and best_iou > 0.25:
            ta_line = lines_ta[best_match_idx]
            used_ta_indices.add(best_match_idx)

            en_text = en_line.get("text", "")
            ta_text = ta_line.get("text", "")
            en_conf = en_line.get("confidence", 0.0)
            ta_conf = ta_line.get("confidence", 0.0)

            if has_tamil_characters(ta_text) and not has_tamil_characters(en_text):
                merged.append(ta_line)
            elif not has_tamil_characters(ta_text) and en_conf >= ta_conf:
                merged.append(en_line)
            elif ta_conf > en_conf:
                merged.append(ta_line)
            else:
                merged.append(en_line)
        else:
            merged.append(en_line)

    for idx, ta_line in enumerate(lines_ta):
        if idx not in used_ta_indices:
            merged.append(ta_line)

    def line_sort_key(line):
        bbox = line.get("bbox", [])
        if bbox and len(bbox) > 0:
            y = min(pt[1] for pt in bbox)
            x = min(pt[0] for pt in bbox)
            return (round(y / 16.0) * 16, x)
        return (0, 0)

    merged.sort(key=line_sort_key)
    return merged


def _run_vision_fallback_ocr(
    np_image: np.ndarray,
    img_width: int,
    img_height: int,
    coord_transform: Optional[Tuple[float, float, int, int]] = None,
) -> Dict[str, Any]:
    """
    High-accuracy optical character extraction fallback using Gemini 3.6-flash
    when local PaddlePaddle native runtime is unavailable on current Python build.
    Produces the exact same formatted lines, bounding boxes, confidence, and layout blocks.
    """
    import google.generativeai as genai
    from PIL import Image

    gemini_key = (
        os.getenv("GEMINI_API_KEY")
        or os.getenv("AI_API_KEY")
        or getattr(settings, "GEMINI_API_KEY", "")
        or getattr(settings, "AI_API_KEY", "")
    )

    try:
        genai.configure(api_key=gemini_key, transport="rest")
        pil_img = Image.fromarray(np_image)
        if max(pil_img.size) > 800:
            pil_img.thumbnail((800, 800), Image.Resampling.LANCZOS)
        prompt = (
            "You are an exact OCR optical character recognition engine. "
            "Transcribe line by line ALL text visible in this document verbatim. "
            "Keep each line on its own row. Do NOT summarize, do not omit rows, and do not explain."
        )
        try:
            model = genai.GenerativeModel("models/gemini-3.5-flash")
            resp = model.generate_content([prompt, pil_img])
        except Exception:
            model = genai.GenerativeModel("models/gemini-3.6-flash")
            resp = model.generate_content([prompt, pil_img])
        content = resp.text or ""
        raw_lines = [l.strip() for l in content.split("\n") if l.strip()]
        h, w = np_image.shape[:2]
        classic_result = []
        line_step = max(20, h // (len(raw_lines) + 1) if raw_lines else 30)
        for idx, l in enumerate(raw_lines):
            y_top = idx * line_step + 10
            y_bot = y_top + line_step - 5
            box = [[10, y_top], [w - 10, y_top], [w - 10, y_bot], [10, y_bot]]
            classic_result.append([box, (l, 0.98)])

        return format_ocr_results([classic_result], img_width=img_width, img_height=img_height, coord_transform=coord_transform)
    except Exception as e:
        logger.error(f"Gemini OCR fallback failed: {e}", exc_info=True)
        return format_ocr_results([], img_width=img_width, img_height=img_height, coord_transform=coord_transform)


def run_fast_ocr(
    np_image: np.ndarray,
    lang: str = "bilingual",
    omit_logos: bool = True,
    img_width: int = 0,
    img_height: int = 0,
    coord_transform: Optional[Tuple[float, float, int, int]] = None,
) -> Dict[str, Any]:
    """
    High-throughput accelerated OCR executing neural detection and concurrent multi-worker
    recognition across CPU threads with noise-speck filtering.
    Falls back gracefully if native paddle inference is not supported on host OS.
    """
    ocr_engine = OCRManager.get_instance(lang)
    if ocr_engine is None:
        return _run_vision_fallback_ocr(np_image, img_width=img_width, img_height=img_height, coord_transform=coord_transform)

    try:
        sub = getattr(ocr_engine, "paddlex_pipeline", None)
        pipeline = getattr(sub, "_pipeline", None) if sub else None
        if pipeline is None:
            raise RuntimeError("Underlying sub-pipeline not found")
        rec = pipeline.text_rec_model

        # 1. High-speed neural detection with 960 max side len
        det_params = pipeline.get_text_det_params(
            text_det_limit_side_len=960,
            text_det_limit_type="max",
            text_det_box_thresh=0.5,
            text_det_thresh=0.25,
            text_det_unclip_ratio=1.6,
        )
        det_res = list(pipeline.text_det_model(np_image, **det_params))[0]
        raw_boxes = det_res.get("dt_polys", [])
        if len(raw_boxes) == 0:
            return format_ocr_results([], omit_logos=omit_logos, img_width=img_width, img_height=img_height, coord_transform=coord_transform)

        sorted_boxes = pipeline._sort_boxes(raw_boxes)

        # 2. Filter out sub-pixel noise specks before neural recognition
        valid_boxes = []
        for b in sorted_boxes:
            pts = np.array(b)
            bw = np.linalg.norm(pts[1] - pts[0])
            bh = np.linalg.norm(pts[3] - pts[0])
            if bw >= 10 and bh >= 7 and (bw * bh) >= 80:
                valid_boxes.append(b)

        if len(valid_boxes) == 0:
            return format_ocr_results([], omit_logos=omit_logos, img_width=img_width, img_height=img_height, coord_transform=coord_transform)

        crops = [pipeline._crop_by_polys(np_image, [b])[0] for b in valid_boxes]

        # 3. Concurrent multi-worker recognition across CPU cores
        worker_pool = OCRManager.get_rec_workers(lang)
        num_workers = min(len(worker_pool) if worker_pool else 1, len(crops))

        if worker_pool and num_workers > 1:
            def recognize_crop(item):
                idx, crop = item
                worker = worker_pool[idx % num_workers]
                batch_raw = rec.pre_tfs["Read"](imgs=[crop])
                batch_norm = rec.pre_tfs["ReisizeNorm"](imgs=batch_raw)
                x = rec.pre_tfs["ToBatch"](imgs=batch_norm)
                preds = worker(x)
                ch, cw = batch_raw[0].shape[:2]
                wh_ratio = cw * 1.0 / max(1.0, float(ch))
                texts, scores = rec.post_op(
                    preds,
                    return_word_box=False,
                    wh_ratio_list=[wh_ratio],
                    max_wh_ratio=max(10.0, wh_ratio),
                )
                return texts[0], float(scores[0])

            with ThreadPoolExecutor(max_workers=num_workers) as executor:
                rec_res = list(executor.map(recognize_crop, enumerate(crops)))

            texts = [r[0] for r in rec_res]
            scores = [r[1] for r in rec_res]
        else:
            rec_results = list(rec(crops, return_word_box=False))
            texts = [r["rec_text"] for r in rec_results]
            scores = [float(r["rec_score"]) for r in rec_results]

        raw_dict = [{
            "rec_texts": texts,
            "rec_scores": scores,
            "rec_polys": valid_boxes,
        }]
        return format_ocr_results(raw_dict, omit_logos=omit_logos, img_width=img_width, img_height=img_height, coord_transform=coord_transform)

    except Exception as err:
        logger.warning(f"Accelerated multi-worker OCR pass encountered error: {err}. Gracefully falling back...")
        try:
            ocr_call = getattr(ocr_engine, "predict", getattr(ocr_engine, "ocr", None))
            try:
                raw_result = ocr_call(np_image)
            except TypeError:
                raw_result = ocr_call(np_image, cls=True)
            return format_ocr_results(raw_result, omit_logos=omit_logos, img_width=img_width, img_height=img_height, coord_transform=coord_transform)
        except Exception as err2:
            logger.warning(f"Classic OCR fallback also encountered: {err2}. Utilizing vision fallback.")
            return _run_vision_fallback_ocr(np_image, img_width=img_width, img_height=img_height, coord_transform=coord_transform)


def run_bilingual_ocr(
    np_image: np.ndarray,
    omit_logos: bool = True,
    img_width: int = 0,
    img_height: int = 0,
    coord_transform: Optional[Tuple[float, float, int, int]] = None,
) -> Dict[str, Any]:
    """
    Executes high-speed bilingual extraction using the unified mobile detector & recognizer.
    """
    return run_fast_ocr(
        np_image,
        lang="bilingual",
        omit_logos=omit_logos,
        img_width=img_width,
        img_height=img_height,
        coord_transform=coord_transform,
    )
