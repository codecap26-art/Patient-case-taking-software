import enum
import uuid
from datetime import datetime, timezone
from typing import Optional, List, Any, TYPE_CHECKING
from sqlalchemy import String, DateTime, ForeignKey, Enum, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

if TYPE_CHECKING:
    from app.db.models.patient import Patient
    from app.db.models.doctor import Doctor
    from app.db.models.clinical_case import ClinicalCase
    from app.db.models.prescription import Prescription


class ConsultationStatus(str, enum.Enum):
    SCHEDULED = "SCHEDULED"
    IN_PROGRESS = "IN_PROGRESS"
    RECORDED = "RECORDED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class Consultation(Base):
    __tablename__ = "consultations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    patient_id: Mapped[str] = mapped_column(String(36), ForeignKey("patients.id", ondelete="CASCADE"), nullable=False, index=True)
    doctor_id: Mapped[str] = mapped_column(String(36), ForeignKey("doctors.id", ondelete="CASCADE"), nullable=False, index=True)
    status: Mapped[ConsultationStatus] = mapped_column(
        Enum(ConsultationStatus),
        default=ConsultationStatus.IN_PROGRESS,
        nullable=False,
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    ended_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    audio_storage_key: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    # Transcript stored as structured JSON list: [{"speaker": "doctor", "text": "...", "start": 0.0, "end": 2.5}]
    transcript: Mapped[Optional[List[dict[str, Any]]]] = mapped_column(JSON, default=list, nullable=True)
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
    patient: Mapped["Patient"] = relationship("Patient", back_populates="consultations")
    doctor: Mapped["Doctor"] = relationship("Doctor", back_populates="consultations")
    clinical_case: Mapped[Optional["ClinicalCase"]] = relationship("ClinicalCase", back_populates="consultation", uselist=False, cascade="all, delete-orphan")
    prescription: Mapped[Optional["Prescription"]] = relationship("Prescription", back_populates="consultation", uselist=False, cascade="all, delete-orphan")
