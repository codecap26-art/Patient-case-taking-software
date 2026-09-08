import enum
import uuid
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any, TYPE_CHECKING
from sqlalchemy import String, DateTime, ForeignKey, Enum, Text, Boolean, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

if TYPE_CHECKING:
    from app.db.models.consultation import Consultation
    from app.db.models.patient import Patient
    from app.db.models.doctor import Doctor


class PrescriptionStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class Prescription(Base):
    __tablename__ = "prescriptions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    consultation_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("consultations.id", ondelete="SET NULL"), unique=True, nullable=True)
    patient_id: Mapped[str] = mapped_column(String(36), ForeignKey("patients.id", ondelete="CASCADE"), nullable=False, index=True)
    doctor_id: Mapped[str] = mapped_column(String(36), ForeignKey("doctors.id", ondelete="CASCADE"), nullable=False, index=True)
    diagnosis_notes: Mapped[str] = mapped_column(Text, nullable=False)
    # Structured medicines JSON list: [{"name": "...", "dosage": "...", "frequency": "...", "duration": "...", "instructions": "..."}]
    medicines: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list, nullable=False)
    general_advice: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    doctor_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    follow_up_date: Mapped[Optional[str]] = mapped_column(String(20), nullable=True) # YYYY-MM-DD
    status: Mapped[PrescriptionStatus] = mapped_column(
        Enum(PrescriptionStatus),
        default=PrescriptionStatus.DRAFT,
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
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
    consultation: Mapped[Optional["Consultation"]] = relationship("Consultation", back_populates="prescription")
    patient: Mapped["Patient"] = relationship("Patient", back_populates="prescriptions")
    doctor: Mapped["Doctor"] = relationship("Doctor", back_populates="prescriptions")
