# Patient Case Taking Software — FastAPI Backend

**SIH Problem Statement**: SIH26-26047  
**Ministry**: Ministry of Ayush  
**Tech Stack**: Python 3.11+, FastAPI, SQLAlchemy 2.0, PostgreSQL / SQLite, Alembic, Pydantic v2, PyJWT, Passlib (bcrypt)

---

## Key Features

1. **Modular Production Architecture**: Clear separation across Database Models, Pydantic Schemas, Domain Services, and REST API Routes.
2. **Strict Role & Consent Authorization**: Role-based access control (`DOCTOR`, `PATIENT`, `ADMIN`), cross-patient data isolation, and granular patient consent validation.
3. **Bedside QR Patient Linking**: Cryptographically signed, short-lived HMAC QR tokens for patient identification.
4. **Consultation & Diarized Transcript Pipeline**: Ingests speaker-diarized transcripts (M2 interface) and feeds structured Clinical Case extraction (M3 interface).
5. **Doctor-Controlled Prescriptions**: Prescriptions require explicit doctor creation and confirmation with structured medication lists.
6. **Secure Document Management**: Multi-format medical document upload, size/MIME validation, and local/S3-ready storage abstraction.
7. **Hospital Interoperability & FHIR**: Standardized hospital adapter architecture (Apollo, Fortis, Ayush Clinic) with FHIR R4 resource conversion (Patient, Encounter, MedicationRequest).
8. **Permission-Aware Doctor AI / RAG**: Provides sourced clinical context queries to assist doctors with clinical disclaimers.
9. **Comprehensive Audit Trail**: Automatically logs logins, record accesses, document views, consent responses, and external queries.

---

## Getting Started

### 1. Prerequisites
- Python 3.11 or higher
- pip and virtualenv

### 2. Virtual Environment Setup
```powershell
cd backend
python -m venv venv
.\venv\Scripts\activate
```

### 3. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 4. Configuration
Review or customize `.env`:
```ini
DATABASE_URL=sqlite:///./app.db
JWT_SECRET_KEY=dev_secret_jwt_key_sih26_patient_case_taking_change_in_production_928374
ACCESS_TOKEN_EXPIRE_MINUTES=120
STORAGE_PATH=./storage/uploads
```

### 5. Seed Initial Development Data
Seeds 1 doctor, 2 patients, sample consultations, prescriptions, documents, and hospital connectors:
```powershell
python -m app.db.seed
```

### 6. Run the FastAPI Server
```powershell
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

---

## Interactive Documentation

- **Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
- **Health Check**: [http://127.0.0.1:8000/api/v1/health](http://127.0.0.1:8000/api/v1/health)

---

## Running Tests

Run the automated test suite with pytest:
```powershell
pytest
```

---

## Test Credentials (from Seed)

| Role | Mobile Number | Password / OTP | Notes |
|---|---|---|---|
| **Doctor** | `9876543200` | `doctor123` | Dr. Priya Sharma (Apollo Clinic) |
| **Patient 1** | `9876543210` | `patient123` or OTP `123456` | Ramesh Kumar (Full records) |
| **Patient 2** | `9876543222` | `patient123` or OTP `123456` | Anita Desai |
