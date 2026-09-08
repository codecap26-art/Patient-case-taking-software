# Patient Case Taking Software – OCR & Doctor AI Integration Architecture
**SIH Problem Statement: SIH26-26047 (Ministry of Ayush)**

---

## 1. Executive Summary

This document specifies the unified integration between two key capabilities developed for the **Patient Case Taking Software**:
1. **Medical Document Scanning & OCR Extraction (Member 1)**
2. **Doctor AI Clinical Assistant & RAG Query Pipeline (Member 2)**

The integration connects the patient-facing document intake pipeline with the clinical decision-support engine on the doctor dashboard through a single, compliant, consent-governed backend.

---

## 2. End-to-End Architecture & Data Flow

```
+-----------------------------------------------------------------------------------+
| PATIENT EXPERIENCE (Mobile / Flutter App & Dashboard)                             |
|                                                                                   |
|  1. Patient uploads medical documents (CBC, Lipid Panel, Blood Sugar, X-Ray)      |
|  2. Calls POST /api/v1/documents/upload                                           |
+------------------------------------------+----------------------------------------+
                                           |
                                           v
+-----------------------------------------------------------------------------------+
| UNIFIED BACKEND PIPELINE (FastAPI + Supabase PostgreSQL)                         |
|                                                                                   |
|  * OCR Integration Client (PaddleOCR client + Clinical Regex/Entity Parser)      |
|    - Normalizes multi-format lab outputs (Hemoglobin, WBC, Platelets, etc.)       |
|    - Populates `extracted_summary`, `structured_data`, and full `raw_ocr_text`    |
|                                                                                   |
|  * Storage & Database Persistence                                                 |
|    - Stored in `documents` table linked to authenticated `patient_id`             |
|    - Processing status updated to `PROCESSED`                                     |
|                                                                                   |
|  * Consent & Authorization Layer                                                 |
|    - Enforces RBAC & explicit Patient Consent before Doctor can view/query docs   |
+--------------------+-------------------------------------+------------------------+
                     |                                     |
                     v                                     v
+--------------------------------------+ +------------------------------------------+
| DOCTOR DASHBOARD - CLINICAL RECORDS  | | DOCTOR AI RAG ASSISTANT PIPELINE         |
|                                      | |                                          |
| * GET /api/v1/patients/              | | * Doctor asks clinical question in       |
|   (List & search patients)           | |   context of selected `patient_id`       |
|                                      | | * POST /api/v1/doctor-ai/query           |
| * GET /api/v1/documents/patient/{id} | | * RAG Engine indexes:                    |
|   (View verified lab metrics, dates, | |   - Diarized consultation transcripts    |
|    hospital sources, summaries)      | |   - Active & historical prescriptions    |
|                                      | |   - OCR extracted documents & lab values |
|                                      | | * Synthesizes clinical summary citing    |
|                                      | |   primary OCR lab source documents       |
|                                      | | * Includes mandatory safety disclaimer   |
+--------------------------------------+ +------------------------------------------+
```

---

## 3. Core API Endpoints

### A. Document Intake & OCR (`/api/v1/documents`)
- **`POST /api/v1/documents/upload`**  
  *Roles*: `PATIENT`, `DOCTOR`, `ADMIN`  
  Uploads a document, triggers OCR parsing, populates structured lab values, and persists to DB.
- **`GET /api/v1/documents/my-documents`**  
  *Roles*: `PATIENT`  
  Returns all medical documents uploaded by the authenticated patient.
- **`GET /api/v1/documents/patient/{patient_id}`**  
  *Roles*: `DOCTOR`, `ADMIN` (Subject to patient consent / active consultation)  
  Retrieves documents and extracted metrics for a specific patient.
- **`POST /api/v1/documents/ocr/extract`**  
  *Roles*: Public / Microservice compatibility  
  Direct OCR extraction endpoint compatible with PaddleOCR microservice requests.

### B. Patient Management (`/api/v1/patients`)
- **`GET /api/v1/patients/`**  
  *Roles*: `DOCTOR`, `ADMIN`  
  Search and list patients with pagination, contact details, and blood group.
- **`GET /api/v1/patients/{patient_id}`**  
  *Roles*: `DOCTOR`, `ADMIN` (Subject to consent)  
  Get comprehensive patient profile and baseline demographics.

### C. Doctor AI Assistant & Conversational Intake (`/api/v1/doctor-ai`)
- **`POST /api/v1/doctor-ai/query`**  
  *Roles*: `DOCTOR` (Subject to patient consent)  
  *Body*: `{"patient_id": "<UUID>", "question": "What are the latest hemoglobin and lipid levels?"}`  
  *Response*: Contextualized clinical summary, document source citations (`source_type: document`, `document_id`, `title`), and clinical safety disclaimer.
- **`POST /api/v1/doctor-ai/conversations/{conversation_id}/message`**  
  *Roles*: Kiosk / Patient / Doctor Clinical Intake  
  *Body*: `{"message": "I have continuous joint pain and dry skin for 3 weeks"}`  
  *Response*: Structured clinical state (`chief_complaint`, `hpi`, `ayush_assessment` including Prakriti/Ahara/Vihara), real-time emergency red-flag symptom detection, and next targeted clinical question.

---

## 4. Key Security & Safety Principles

1. **AI as Assistant**: Doctor AI strictly aids clinical review and **never** makes autonomous diagnoses or prescriptions.
2. **Consent & RBAC**: Doctors can only access medical documents and query Doctor AI for patients who have granted active consent (`ConsentStatus.GRANTED`) or have an ongoing consultation.
3. **Traceable Citations**: Every answer generated by Doctor AI references specific consultation sessions, prescriptions, or OCR document IDs.
4. **Safety Disclaimer**: All AI responses include an explicit clinical validation disclaimer.

---

## 5. Verification & Test Coverage

The integration is covered by end-to-end automated pytest suites in `tests/test_ocr_doctor_ai_integration.py`:
- `test_patient_upload_document_and_ocr_extraction`: Verifies upload and OCR entity extraction.
- `test_patient_get_my_documents`: Verifies patient retrieval of uploaded records.
- `test_doctor_list_patients_and_view_patient_documents`: Verifies doctor listing patients and viewing documents under consent.
- `test_doctor_ai_query_with_ocr_document_citation`: Verifies Doctor AI queries retrieving and citing OCR lab documents.
- `test_direct_ocr_compatibility_endpoint`: Verifies compatibility with PaddleOCR API format.
- `test_cross_patient_unauthorized_document_access`: Verifies 403 Forbidden enforcement on unauthorized cross-patient document requests.
