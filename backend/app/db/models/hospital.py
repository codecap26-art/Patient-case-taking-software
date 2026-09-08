import uuid
from datetime import datetime, timezone
from typing import List, TYPE_CHECKING
from sqlalchemy import String, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

if TYPE_CHECKING:
    from app.db.models.doctor import Doctor
    from app.db.models.medical_record import MedicalRecord


class Hospital(Base):
    __tablename__ = "hospitals"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    code: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False) # e.g. HOSP_A, HOSP_B
    base_url: Mapped[str] = mapped_column(String(255), nullable=False)
    integration_type: Mapped[str] = mapped_column(String(50), default="FHIR_REST", nullable=False) # FHIR_REST, CUSTOM_JSON, AYUSH_HUB
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    doctors: Mapped[List["Doctor"]] = relationship("Doctor", back_populates="hospital")
    medical_records: Mapped[List["MedicalRecord"]] = relationship("MedicalRecord", back_populates="hospital")
