from typing import List, Union, Optional
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    APP_NAME: str = "Patient Case Taking API"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = "development"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"

    # Database
    DATABASE_URL: str = "sqlite:///./app.db"

    # Security & Tokens
    JWT_SECRET_KEY: str = "default_jwt_secret_key_change_in_production_sih26"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    QR_SIGNING_SECRET: str = "default_qr_secret_change_in_production"

    # CORS
    CORS_ORIGINS: Union[str, List[str]] = ["*"]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # Storage
    STORAGE_PATH: str = "./storage/uploads"
    MAX_UPLOAD_SIZE_MB: int = 25
    ALLOWED_MIME_TYPES: List[str] = [
        "application/pdf",
        "image/jpeg",
        "image/png",
        "image/webp",
        "text/plain",
    ]

    # Integration & AI flags
    MOCK_EXTERNAL_SERVICES: bool = False
    AI_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    LLM_API_KEY: str = ""
    AI_MODEL: str = "gemini-2.0-flash"
    GROQ_API_KEY: Optional[str] = None
    GROQ_MODEL: str = "llama-3.3-70b-versatile"


settings = Settings()
