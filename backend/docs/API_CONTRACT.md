# Patient Case Taking Platform — API Contract Specification

**SIH Problem Statement**: SIH26-26047 (Ministry of Ayush)  
**API Base URL**: `http://localhost:8000/api/v1`  
**Interactive Swagger Docs**: `http://localhost:8000/docs`  
**Authentication Scheme**: HTTP Bearer (`Authorization: Bearer <JWT_ACCESS_TOKEN>`)

---

## 1. System Health & Metadata

### `GET /health`
- **Auth**: None
- **Response `200 OK`**:
```json
{
  "status": "healthy",
  "app": "Patient Case Taking API",
  "version": "1.0.0",
  "environment": "development",
  "database": "connected"
}
```

---

## 2. Authentication (`/auth`)

### `POST /auth/register`
- **Auth**: None
- **Request**:
```json
{
  "phone": "9876543210",
  "password": "patient_password_123",
  "first_name": "Ramesh",
  "last_name": "Kumar",
  "email": "ramesh.kumar@healthmail.com",
  "role": "PATIENT",
  "date_of_birth": "1984-06-15",
  "gender": "Male",
  "blood_group": "O+",
  "address": "Flat 402, Green Meadows Residency, Outer Ring Road, Bengaluru - 560103",
  "emergency_contact": "9876543211"
}
```
- **Response `201 Created`**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 7200,
  "user_id": "u-uuid-1",
  "role": "PATIENT",
  "patient_id": "p-uuid-1",
  "doctor_id": null
}
```

### `POST /auth/login`
- **Auth**: None
- **Request (Password or OTP)**:
```json
{
  "phone": "9876543210",
  "password": "patient_password_123",
  "otp": "123456"
}
```
- **Response `200 OK`**: TokenResponse

### `POST /auth/send-otp`
- **Request**: `{"phone": "9876543210"}`
- **Response `200 OK`**: `{"status": "success", "message": "OTP sent successfully."}`

### `GET /auth/me`
- **Auth**: Required (`PATIENT`, `DOCTOR`, `ADMIN`)
- **Response `200 OK`**: Current user details and linked patient/doctor record.

---

## 3. Patients (`/patients`)

### `GET /patients/me`
- **Auth**: Required (`PATIENT`)
- **Response `200 OK`**: Full demographic profile of logged-in patient.

### `GET /patients/{id}`
- **Auth**: Required (Owner Patient or Doctor with active consent)
- **Response `200 OK`**: Patient profile.

### `PUT /patients/{id}`
- **Auth**: Required (Owner Patient)
- **Request**:
```json
{
  "address": "12th Main, Indiranagar, Bengaluru",
  "emergency_contact": "9876543299",
  "allergies": ["Penicillin", "Dust Mites"]
}
```

### `GET /patients/{id}/history?page=1&limit=20`
- **Auth**: Required (Owner or Authorized Doctor)
- **Response `200 OK`**:
```json
{
  "items": [
    {
      "id": "rec-1",
      "title": "Acute Upper Respiratory Tract Infection",
      "record_type": "Consultation",
      "provider": "Dr. Priya Sharma, Apollo Clinic",
      "year": "2026",
      "recorded_at": "2026-02-24",
      "data": {"BP": "124/82 mmHg", "Pulse": "78 bpm"}
    }
  ],
  "page": 1,
  "limit": 20,
  "total": 1,
  "total_pages": 1
}
```

### `GET /patients/{id}/documents?page=1&limit=20`
- **Auth**: Required (Owner or Authorized Doctor)

### `GET /patients/{id}/prescriptions?page=1&limit=20&active_only=false`
- **Auth**: Required (Owner or Authorized Doctor)

### `GET /patients/{id}/consultations?page=1&limit=20`
- **Auth**: Required (Owner or Authorized Doctor)

### `POST /patients/{id}/qr-token`
- **Auth**: Required
- **Response `200 OK`**:
```json
{
  "qr_payload": "PCT:v1:p-uuid-1:1741285000:7f92a10b42c8d193",
  "patient_id": "p-uuid-1",
  "expires_in_seconds": 300
}
```

### `POST /patients/qr/link`
- **Auth**: Required (`DOCTOR`)
- **Request**: `{"qr_payload": "PCT:v1:p-uuid-1:1741285000:7f92a10b42c8d193"}`
- **Response `200 OK`**: Linked Patient record.

---

## 4. Consultations & Transcripts (`/consultations`)

### `POST /consultations`
- **Auth**: Required (`DOCTOR`)
- **Request**: `{"patient_id": "p-uuid-1"}`

### `POST /consultations/{id}/transcript`
- **Module Interface**: **M2 (Audio/STT) -> Backend**
- **Auth**: Required
- **Request**:
```json
{
  "language": "en",
  "audio_storage_key": "audio/session_101.wav",
  "transcript": [
    {"speaker": "doctor", "text": "What symptoms do you have?", "start": 0.0, "end": 2.5},
    {"speaker": "patient", "text": "I have sore throat and cough.", "start": 2.8, "end": 6.1}
  ]
}
```

---

## 5. Clinical Cases (`/clinical-cases`)

### `POST /clinical-cases`
- **Module Interface**: **M3 (Clinical Extraction) -> Backend**
- **Auth**: Required

### `POST /clinical-cases/{id}/confirm`
- **Auth**: Required (`DOCTOR`)
- **Request**: `{"doctor_notes": "Diagnosis confirmed: Viral Pharyngitis."}`
- **Response `200 OK`**: Updates status to `CONFIRMED`.

---

## 6. Prescriptions (`/prescriptions`)

### `POST /prescriptions`
- **Auth**: Required (`DOCTOR`)
- **Request**:
```json
{
  "patient_id": "p-uuid-1",
  "consultation_id": "cons-uuid-1",
  "diagnosis_notes": "Acute Pharyngitis",
  "medicines": [
    {
      "name": "Tab. Paracetamol 650mg",
      "dosage": "650 mg",
      "frequency": "1-0-1",
      "duration": "3 Days",
      "timing": "After food",
      "instructions": "When body temperature > 99.5°F"
    }
  ],
  "general_advice": "Hydrate and avoid chilled drinks.",
  "follow_up_date": "2026-03-02"
}
```

### `POST /prescriptions/{id}/confirm`
- **Auth**: Required (`DOCTOR`)

---

## 7. Medical Documents (`/documents`)

### `POST /documents/upload`
- **Auth**: Required (`PATIENT`, `DOCTOR`)
- **Format**: `multipart/form-data`
- **Fields**:
  - `title`: "Complete Blood Count"
  - `document_type`: "Blood Test Report"
  - `hospital_name`: "Apollo Speciality Diagnostics"
  - `document_date`: "2026-02-18"
  - `patient_id`: Optional (defaults to current user)
  - `file`: Binary file (PDF, JPG, PNG)

---

## 8. Consent & Access Control (`/consent`)

### `POST /consent/requests`
- **Auth**: Required (`DOCTOR`)
- **Request**:
```json
{
  "patient_id": "p-uuid-1",
  "provider_name": "Manipal Hospital Whitefield",
  "provider_type": "Multi-Specialty Hospital",
  "purpose": "Specialist Consultation",
  "requested_scope": "Medical History + Previous Prescriptions & Lab Reports",
  "valid_until": "30 Days"
}
```

### `GET /consent/requests`
- **Auth**: Required (`PATIENT`) -> Returns pending consent authorization requests.

### `POST /consent/requests/{id}/respond`
- **Auth**: Required (`PATIENT`)
- **Request**: `{"allow": true}`

### `POST /consent/active/{id}/revoke`
- **Auth**: Required (`PATIENT`) -> Revokes active consent.

---

## 9. Interoperability & Hospital FHIR (`/interoperability`)

### `GET /interoperability/hospitals`
- **Auth**: Required -> Returns list of connected hospitals (Apollo, Fortis, Ayush Clinic).

### `GET /interoperability/patients/{patient_id}/external-records`
- **Auth**: Required (Doctor with consent / Patient owner)
- **Response `200 OK`**: Returns standardized external records retrieved on-demand from hospital adapters.

---

## 10. Doctor AI Clinical Assistant (`/doctor-ai`)

### `POST /doctor-ai/query`
- **Module Interface**: **M6 (RAG & Doctor AI) -> Backend**
- **Auth**: Required (`DOCTOR`)
- **Request**:
```json
{
  "patient_id": "p-uuid-1",
  "question": "What active medications and known drug allergies does this patient have?"
}
```
- **Response `200 OK`**:
```json
{
  "patient_id": "p-uuid-1",
  "question": "What active medications and known drug allergies does this patient have?",
  "answer": "Active medication: Tab. Telmisartan 40mg. CRITICAL WARNING: Known severe allergy to Penicillin.",
  "clinical_disclaimer": "AI Assistant summary is for clinical reference only. The consulting doctor remains solely responsible for diagnosis, treatment decisions, and prescriptions.",
  "sources": [
    {
      "source_type": "prescription",
      "id": "rx-1",
      "title": "Prescription for Stage 1 Hypertension Maintenance",
      "snippet": "Tab. Telmisartan 40mg (Morning after breakfast)"
    }
  ],
  "generated_at": "2026-09-06T17:45:00Z"
}
```

---

## Standard Error Format

All error responses adhere to the standard envelope:
```json
{
  "detail": {
    "code": "CONSENT_REQUIRED",
    "message": "Access to patient p-uuid-1 requires active consent for scope 'read'.",
    "details": {
      "patient_id": "p-uuid-1",
      "required_scope": "read"
    }
  }
}
```
