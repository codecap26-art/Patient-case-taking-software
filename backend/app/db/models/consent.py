import enum
import uuid
from datetime import datetime, timezone
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, DateTime, ForeignKey, Enum, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

if TYPE_CHECKING:
    from app.db.models.patient import Patient


class ConsentStatus(str, enum.Enum):
    PENDING = "PENDING"
    GRANTED = "GRANTED"
    DENIED = "DENIED"
    REVOKED = "REVOKED"
    EXPIRED = "EXPIRED"


class Consent(Base):
    __tablename__ = "consents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    patient_id: Mapped[str] = mapped_column(String(36), ForeignKey("patients.id", ondelete="CASCADE"), nullable=False, index=True)
    provider_name: Mapped[str] = mapped_column(String(200), nullable=False) # Hospital/Doctor requesting
    provider_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True) # Multi-Specialty Hospital, Clinic, Lab
    doctor_name: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    purpose: Mapped[str] = mapped_column(Text, nullable=False) # e.g. Specialist Consultation & Clinical Case Assessment
    requested_scope: Mapped[str] = mapped_column(String(255), nullable=False) # e.g. "Full Medical Timeline + Active Medications" or "ALL"
    status: Mapped[ConsentStatus] = mapped_column(
        Enum(ConsentStatus),
        default=ConsentStatus.PENDING,
        nullable=False,
    )
    request_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    response_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    valid_until: Mapped[Optional[str]] = mapped_column(String(50), nullable=True) # e.g. "24 Hours", "30 Days", "2026-10-01"
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    revoked_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    patient: Mapped["Patient"] = relationship("Patient", back_populates="consents")
