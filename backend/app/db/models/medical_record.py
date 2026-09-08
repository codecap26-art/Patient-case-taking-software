import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any, TYPE_CHECKING
from sqlalchemy import String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

if TYPE_CHECKING:
    from app.db.models.patient import Patient
    from app.db.models.hospital import Hospital


class MedicalRecord(Base):
    __tablename__ = "medical_records"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    patient_id: Mapped[str] = mapped_column(String(36), ForeignKey("patients.id", ondelete="CASCADE"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    source_type: Mapped[str] = mapped_column(String(50), default="CURRENT_SYSTEM", nullable=False) # CURRENT_SYSTEM, UPLOADED_DOCUMENT, EXTERNAL_HOSPITAL
    source_hospital_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("hospitals.id", ondelete="SET NULL"), nullable=True)
    external_record_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    record_type: Mapped[str] = mapped_column(String(50), nullable=False) # Consultation, Lab Test, Hospitalization, Surgery, Immunization
    provider: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    diagnosis: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    year: Mapped[Optional[str]] = mapped_column(String(10), nullable=True) # e.g. "2026"
    recorded_at: Mapped[Optional[str]] = mapped_column(String(50), nullable=True) # e.g. "2026-02-24"
    data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, default=dict, nullable=True) # Vitals, findings, lab parameters
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    patient: Mapped["Patient"] = relationship("Patient", back_populates="medical_records")
    hospital: Mapped[Optional["Hospital"]] = relationship("Hospital", back_populates="medical_records")
