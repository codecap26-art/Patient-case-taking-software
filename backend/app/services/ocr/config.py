import os
from typing import Dict, List
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseModel):
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", 8000))
    CORS_ORIGINS: List[str] = [
        origin.strip()
        for origin in os.getenv(
            "CORS_ORIGINS",
            "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173,*",
        ).split(",")
    ]
    MAX_FILE_SIZE_BYTES: int = int(os.getenv("MAX_FILE_SIZE_BYTES", 20 * 1024 * 1024))  # 20 MB
    MAX_IMAGE_DIMENSION: int = int(os.getenv("MAX_IMAGE_DIMENSION", 1400))  # Max width/height for fast CPU inference
    CONTRAST_ENHANCE_FACTOR: float = float(os.getenv("CONTRAST_ENHANCE_FACTOR", 1.15))
    DEFAULT_LANGUAGE: str = os.getenv("DEFAULT_LANGUAGE", "bilingual")
    OCR_ENABLED: bool = os.getenv("OCR_ENABLED", "true").lower() in ("true", "1", "yes")

    ALLOWED_MIME_TYPES: List[str] = [
        "image/png",
        "image/jpeg",
        "image/jpg",
        "image/webp",
        "application/pdf",
    ]

    SUPPORTED_LANGUAGES: Dict[str, str] = {
        "bilingual": "English + Tamil (Bilingual)",
        "en": "English",
        "ta": "Tamil",
    }


settings = Settings()
