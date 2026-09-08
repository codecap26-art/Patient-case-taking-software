import enum
import uuid
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any, TYPE_CHECKING
from sqlalchemy import String, DateTime, ForeignKey, Enum, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

if TYPE_CHECKING:
    from app.db.models.consultation import Consultation
    from app.db.models.patient import Patient


class ClinicalCaseStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    REVIEWED = "REVIEWED"
    CONFIRMED = "CONFIRMED"


class ClinicalCase(Base):
    __tablename__ = "clinical_cases"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    consultation_id: Mapped[str] = mapped_column(String(36), ForeignKey("consultations.id", ondelete="CASCADE"), unique=True, nullable=False)
    patient_id: Mapped[str] = mapped_column(String(36), ForeignKey("patients.id", ondelete="CASCADE"), nullable=False, index=True)
    status: Mapped[ClinicalCaseStatus] = mapped_column(
        Enum(ClinicalCaseStatus),
        default=ClinicalCaseStatus.DRAFT,
        nullable=False,
    )
    symptoms: Mapped[Optional[List[str]]] = mapped_column(JSON, default=list, nullable=True)
    complaints: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    duration: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    medical_history: Mapped[Optional[List[str]]] = mapped_column(JSON, default=list, nullable=True)
    allergies: Mapped[Optional[List[str]]] = mapped_column(JSON, default=list, nullable=True)
    medications: Mapped[Optional[List[str]]] = mapped_column(JSON, default=list, nullable=True)
    family_history: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    examination: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, default=dict, nullable=True) # Vitals, physical signs
    extracted_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, default=dict, nullable=True) # Full LLM output
    doctor_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    confirmed_by_doctor_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    confirmed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
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
    consultation: Mapped["Consultation"] = relationship("Consultation", back_populates="clinical_case")
    patient: Mapped["Patient"] = relationship("Patient", back_populates="clinical_cases")
