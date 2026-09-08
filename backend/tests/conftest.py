import pytest
from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.base import Base
from app.db.database import get_db
from app.core.security import create_access_token, get_password_hash
from app.db.models import User, UserRole, Patient, Doctor, Hospital, Consent, ConsentStatus

# In-memory SQLite engine for tests
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="function")
def db() -> Generator[Session, None, None]:
    Base.metadata.create_all(bind=test_engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def client(db: Session) -> Generator[TestClient, None, None]:
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def test_hospital(db: Session) -> Hospital:
    hosp = Hospital(
        name="Apollo Speciality Diagnostics",
        code="HOSP_A_APOLLO",
        base_url="https://api.apollo-diagnostics.internal/fhir",
        integration_type="REST_JSON",
        is_active=True,
    )
    db.add(hosp)
    db.commit()
    db.refresh(hosp)
    return hosp


@pytest.fixture(scope="function")
def doctor_user(db: Session, test_hospital: Hospital) -> tuple[User, Doctor, str]:
    user = User(
        email="doctor@test.com",
        phone="9876543200",
        password_hash=get_password_hash("doctor123"),
        role=UserRole.DOCTOR,
        is_active=True,
    )
    db.add(user)
    db.flush()

    doctor = Doctor(
        user_id=user.id,
        doctor_identifier="DOC-TEST-101",
        name="Dr. Priya Sharma",
        specialization="General Physician",
        registration_number="REG-DOC-101",
        hospital_id=test_hospital.id,
    )
    db.add(doctor)
    db.commit()
    db.refresh(user)
    db.refresh(doctor)

    token = create_access_token(
        subject=user.id,
        role=user.role.value,
        extra_claims={"doctor_id": doctor.id},
    )
    return user, doctor, token


@pytest.fixture(scope="function")
def patient_user(db: Session) -> tuple[User, Patient, str]:
    user = User(
        email="patient@test.com",
        phone="9876543210",
        password_hash=get_password_hash("patient123"),
        role=UserRole.PATIENT,
        is_active=True,
    )
    db.add(user)
    db.flush()

    patient = Patient(
        user_id=user.id,
        patient_identifier="PCT-PAT-88492",
        first_name="Ramesh",
        last_name="Kumar",
        phone="9876543210",
        email="patient@test.com",
        date_of_birth="1984-06-15",
        gender="Male",
        blood_group="O+",
    )
    db.add(patient)
    db.commit()
    db.refresh(user)
    db.refresh(patient)

    token = create_access_token(
        subject=user.id,
        role=user.role.value,
        extra_claims={"patient_id": patient.id},
    )
    return user, patient, token


@pytest.fixture(scope="function")
def patient_user_2(db: Session) -> tuple[User, Patient, str]:
    user = User(
        email="patient2@test.com",
        phone="9876543299",
        password_hash=get_password_hash("patient123"),
        role=UserRole.PATIENT,
        is_active=True,
    )
    db.add(user)
    db.flush()

    patient = Patient(
        user_id=user.id,
        patient_identifier="PCT-PAT-99999",
        first_name="Anita",
        last_name="Desai",
        phone="9876543299",
        email="patient2@test.com",
        date_of_birth="1992-11-20",
        gender="Female",
        blood_group="B+",
    )
    db.add(patient)
    db.commit()
    db.refresh(user)
    db.refresh(patient)

    token = create_access_token(
        subject=user.id,
        role=user.role.value,
        extra_claims={"patient_id": patient.id},
    )
    return user, patient, token
