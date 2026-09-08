import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.core.config import settings
from app.core.exceptions import AppException
from app.api.router import api_router
from app.db.database import engine
from app.db.base import Base
# Ensure all models are imported so Base.metadata knows about all tables
import app.db.models # noqa: F401

# Setup structured logging
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("patient_case_taking_api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up %s (version %s, env: %s)...", settings.APP_NAME, settings.APP_VERSION, settings.APP_ENV)
    # Create DB tables if they don't exist (for local SQLite/dev; Alembic handles formal migrations)
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables initialized successfully.")
    except Exception as e:
        logger.error("Database table initialization error: %s", e)
    yield
    logger.info("Shutting down %s...", settings.APP_NAME)


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "Production-grade FastAPI backend for the Patient Case Taking Software "
        "(SIH Problem Statement SIH26-26047, Ministry of Ayush).\n\n"
        "Features:\n"
        "- Secure Patient & Doctor JWT Authentication\n"
        "- Bedside QR Patient Identity Linking\n"
        "- Consultation Session & Speaker-aware Diarized Transcripts\n"
        "- Structured Clinical Case Extraction & Doctor Review/Confirmation\n"
        "- Doctor Prescriptions & Medication Management\n"
        "- Medical Document Storage & OCR Processing\n"
        "- Granular Patient Consent & Access Control\n"
        "- Hospital Interoperability & FHIR R4 Integration\n"
        "- Permission-Aware Doctor AI Clinical Assistant & RAG\n"
        "- Comprehensive Audit Logging"
    ),
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"^https?://.*$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)


# Exception Handlers
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.detail,
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    clean_errors = [{"field": " -> ".join([str(loc) for loc in err["loc"]]), "message": err["msg"]} for err in errors]
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": {
                "code": "VALIDATION_ERROR",
                "message": "Request payload validation failed.",
                "details": clean_errors,
            }
        },
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled exception: %s", exc, exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected server error occurred. Please try again later.",
            }
        },
    )


# Register API v1 Router
app.include_router(api_router, prefix=settings.API_V1_PREFIX)

# Direct /api prefix mount for SIH_OCR /api/ocr/extract endpoint compatibility
from app.api.routes import ocr
app.include_router(ocr.router, prefix="/api")


@app.get("/", tags=["Root"])
def root():
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": f"{settings.API_V1_PREFIX}/health",
    }
