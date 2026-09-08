import uuid
from datetime import datetime, timezone
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

if TYPE_CHECKING:
    from app.db.models.user import User
    from app.db.models.hospital import Hospital
    from app.db.models.consultation import Consultation
    from app.db.models.prescription import Prescription


class Doctor(Base):
    __tablename__ = "doctors"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    doctor_identifier: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False) # e.g. DOC-IND-1049
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    specialization: Mapped[str] = mapped_column(String(150), nullable=False)
    registration_number: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    hospital_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("hospitals.id", ondelete="SET NULL"), nullable=True)
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
    user: Mapped["User"] = relationship("User", back_populates="doctor")
    hospital: Mapped[Optional["Hospital"]] = relationship("Hospital", back_populates="doctors")
    consultations: Mapped[List["Consultation"]] = relationship("Consultation", back_populates="doctor")
    prescriptions: Mapped[List["Prescription"]] = relationship("Prescription", back_populates="doctor")
