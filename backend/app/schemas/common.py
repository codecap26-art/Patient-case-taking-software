from typing import Any, Optional, Generic, TypeVar
from pydantic import BaseModel
from app.utils.pagination import PaginatedResponse

T = TypeVar("T")


class StatusResponse(BaseModel):
    status: str = "success"
    message: str


class ErrorDetail(BaseModel):
    code: str
    message: str
    details: Optional[Any] = None


class ErrorResponse(BaseModel):
    detail: ErrorDetail


class HealthResponse(BaseModel):
    status: str = "healthy"
    app: str
    version: str
    environment: str
    database: str
