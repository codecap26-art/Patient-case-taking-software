import uuid
from datetime import datetime, timezone
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

if TYPE_CHECKING:
    from app.db.models.user import User
    from app.db.models.consultation import Consultation
    from app.db.models.clinical_case import ClinicalCase
    from app.db.models.prescription import Prescription
    from app.db.models.document import Document
    from app.db.models.medical_record import MedicalRecord
    from app.db.models.consent import Consent


class Patient(Base):
    __tablename__ = "patients"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    patient_identifier: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False) # e.g. PCT-PAT-88492
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    date_of_birth: Mapped[Optional[str]] = mapped_column(String(20), nullable=True) # YYYY-MM-DD
    gender: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    blood_group: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    phone: Mapped[str] = mapped_column(String(20), index=True, nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    emergency_contact: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    allergies: Mapped[Optional[List[str]]] = mapped_column(JSON, default=list, nullable=True)
    chronic_conditions: Mapped[Optional[List[str]]] = mapped_column(JSON, default=list, nullable=True)
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
    user: Mapped["User"] = relationship("User", back_populates="patient")
    consultations: Mapped[List["Consultation"]] = relationship("Consultation", back_populates="patient", cascade="all, delete-orphan")
    clinical_cases: Mapped[List["ClinicalCase"]] = relationship("ClinicalCase", back_populates="patient", cascade="all, delete-orphan")
    prescriptions: Mapped[List["Prescription"]] = relationship("Prescription", back_populates="patient", cascade="all, delete-orphan")
    documents: Mapped[List["Document"]] = relationship("Document", back_populates="patient", cascade="all, delete-orphan")
    medical_records: Mapped[List["MedicalRecord"]] = relationship("MedicalRecord", back_populates="patient", cascade="all, delete-orphan")
    consents: Mapped[List["Consent"]] = relationship("Consent", back_populates="patient", cascade="all, delete-orphan")
