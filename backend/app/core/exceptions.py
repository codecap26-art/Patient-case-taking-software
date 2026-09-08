from typing import Any, Optional
from fastapi import HTTPException, status


class AppException(HTTPException):
    def __init__(
        self,
        status_code: int,
        code: str,
        message: str,
        details: Optional[Any] = None,
    ):
        super().__init__(
            status_code=status_code,
            detail={
                "code": code,
                "message": message,
                "details": details,
            },
        )


class NotFoundException(AppException):
    def __init__(self, resource: str, identifier: Any = None):
        msg = f"{resource} not found" if identifier is None else f"{resource} with identifier '{identifier}' not found"
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            code=f"{resource.upper().replace(' ', '_')}_NOT_FOUND",
            message=msg,
        )


class UnauthorizedException(AppException):
    def __init__(self, message: str = "Invalid credentials or unauthenticated"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            code="UNAUTHORIZED",
            message=message,
        )


class ForbiddenException(AppException):
    def __init__(self, message: str = "Permission denied for this resource"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            code="FORBIDDEN",
            message=message,
        )


class ConsentRequiredException(AppException):
    def __init__(self, patient_id: str, scope: str = "all"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            code="CONSENT_REQUIRED",
            message=f"Access to patient {patient_id} requires active consent for scope '{scope}'.",
            details={"patient_id": patient_id, "required_scope": scope},
        )


class ConflictException(AppException):
    def __init__(self, message: str, code: str = "CONFLICT"):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            code=code,
            message=message,
        )


class ValidationException(AppException):
    def __init__(self, message: str, details: Optional[Any] = None):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            code="VALIDATION_ERROR",
            message=message,
            details=details,
        )
