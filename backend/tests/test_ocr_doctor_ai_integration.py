import io
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.db.models.user import User, UserRole
from app.db.models.patient import Patient
from app.db.models.document import Document, DocumentProcessingStatus
from app.core.security import get_password_hash


def test_patient_upload_document_and_ocr_extraction(client: TestClient, patient_user: tuple):
    _, _, token = patient_user
    headers = {"Authorization": f"Bearer {token}"}

    # Patient uploads Blood Test PDF/Image
    fake_file = io.BytesIO(b"Fake complete blood count report content with Hemoglobin 13.8 g/dL and WBC 7400")
    files = {"file": ("complete_blood_count.pdf", fake_file, "application/pdf")}
    data = {
        "title": "Complete Blood Count (CBC) Report",
        "document_type": "Blood Test",
        "hospital_name": "Apollo Diagnostics",
        "document_date": "2026-09-05",
    }

    resp = client.post("/api/v1/documents/upload", headers=headers, data=data, files=files)
    assert resp.status_code == 201
    doc = resp.json()
    assert doc["title"] == "Complete Blood Count (CBC) Report"
    assert doc["processing_status"] == "PROCESSED"
    assert "Hemoglobin" in str(doc.get("structured_data", {}))
    assert doc["hospital_name"] == "Apollo Diagnostics"


def test_patient_get_my_documents(client: TestClient, patient_user: tuple):
    _, _, token = patient_user
    headers = {"Authorization": f"Bearer {token}"}

    # First upload a document
    fake_file = io.BytesIO(b"Sample document content")
    files = {"file": ("my_report.pdf", fake_file, "application/pdf")}
    data = {
        "title": "My Routine Health Report",
        "document_type": "Health Checkup",
    }
    client.post("/api/v1/documents/upload", headers=headers, data=data, files=files)

    resp = client.get("/api/v1/documents/my-documents", headers=headers)
    assert resp.status_code == 200
    docs = resp.json()
    assert isinstance(docs, list)
    assert len(docs) >= 1


def test_doctor_list_patients_and_view_patient_documents(client: TestClient, doctor_user: tuple, patient_user: tuple, db: Session):
    _, _, doc_token = doctor_user
    _, patient, _ = patient_user
    doc_headers = {"Authorization": f"Bearer {doc_token}"}

    # Grant consent for this patient
    from app.db.models.consent import Consent, ConsentStatus
    consent = Consent(
        patient_id=patient.id,
        provider_name="Apollo Clinic",
        doctor_name="Dr. Priya Sharma",
        purpose="Clinical Review",
        requested_scope="read_documents",
        status=ConsentStatus.GRANTED,
    )
    db.add(consent)
    db.commit()

    # Doctor lists all patients
    resp = client.get("/api/v1/patients/", headers=doc_headers)
    assert resp.status_code == 200
    result = resp.json()
    assert "items" in result
    assert len(result["items"]) >= 1

    # Doctor views patient documents
    doc_resp = client.get(f"/api/v1/documents/patient/{patient.id}", headers=doc_headers)
    assert doc_resp.status_code == 200
    docs = doc_resp.json()
    assert "items" in docs


def test_doctor_ai_query_with_ocr_document_citation(client: TestClient, doctor_user: tuple, patient_user: tuple, db: Session):
    _, _, doc_token = doctor_user
    _, patient, _ = patient_user
    doc_headers = {"Authorization": f"Bearer {doc_token}"}

    # Grant consent for this patient
    from app.db.models.consent import Consent, ConsentStatus
    consent = Consent(
        patient_id=patient.id,
        provider_name="Apollo Clinic",
        doctor_name="Dr. Priya Sharma",
        purpose="Doctor AI Clinical Query",
        requested_scope="doctor_ai_rag",
        status=ConsentStatus.GRANTED,
    )
    db.add(consent)

    # Add an OCR document directly to patient
    doc = Document(
        patient_id=patient.id,
        title="Recent Blood Investigation",
        document_type="Blood Report",
        hospital_name="Apollo Clinic",
        document_date="2026-09-05",
        file_name="blood_test.pdf",
        mime_type="application/pdf",
        file_size_bytes=2048,
        file_size_display="2 KB",
        storage_key="documents/blood_test.pdf",
        processing_status=DocumentProcessingStatus.PROCESSED,
        extracted_summary="CBC Report: Hemoglobin 13.8 g/dL, WBC 7,400 /uL, Platelets 240,000 /uL",
        structured_data={"Hemoglobin": "13.8 g/dL", "WBC": "7,400 /uL"},
    )
    db.add(doc)
    db.commit()

    # Doctor queries Doctor AI about lab results for this patient
    payload = {
        "patient_id": patient.id,
        "question": "What were the latest blood test results and hemoglobin levels?",
    }
    resp = client.post("/api/v1/doctor-ai/query", headers=doc_headers, json=payload)
    assert resp.status_code == 200
    ai_resp = resp.json()
    assert ai_resp["patient_id"] == patient.id
    assert "Disclaimer" in ai_resp["answer"]
    assert len(ai_resp["sources"]) >= 1
    # Check that at least one source is a document
    doc_sources = [s for s in ai_resp["sources"] if s["source_type"] == "document"]
    assert len(doc_sources) >= 1


def test_direct_ocr_compatibility_endpoint(client: TestClient):
    fake_file = io.BytesIO(b"Sample diagnostic image content")
    files = {"file": ("blood_report_scan.jpg", fake_file, "image/jpeg")}
    resp = client.post("/api/v1/documents/ocr/extract?lang=en", files=files)
    assert resp.status_code == 200
    ocr_result = resp.json()
    assert ocr_result["success"] is True
    assert "text" in ocr_result
    assert "lines" in ocr_result
    assert "confidence" in ocr_result


def test_cross_patient_unauthorized_document_access(client: TestClient, patient_user: tuple, patient_user_2: tuple, db: Session):
    _, _, patient_1_token = patient_user
    _, patient_2, _ = patient_user_2
    p1_headers = {"Authorization": f"Bearer {patient_1_token}"}

    # Create document belonging to patient 2
    secret_doc = Document(
        patient_id=patient_2.id,
        title="Confidential Diagnostic Report",
        document_type="Blood Report",
        file_name="confidential.pdf",
        mime_type="application/pdf",
        file_size_bytes=1024,
        file_size_display="1 KB",
        storage_key="documents/confidential.pdf",
        processing_status=DocumentProcessingStatus.PROCESSED,
    )
    db.add(secret_doc)
    db.commit()

    # Patient 1 attempts to access Patient 2's document -> Must be 403 Forbidden
    forbidden_resp = client.get(f"/api/v1/documents/{secret_doc.id}", headers=p1_headers)
    assert forbidden_resp.status_code == 403


def test_interactive_conversational_intake_with_emergency_detection(client: TestClient):
    conv_id = "test-conv-123"

    # Step 1: Chief complaint
    resp1 = client.post(
        f"/api/v1/doctor-ai/conversations/{conv_id}/message",
        json={"message": "I have been having continuous knee joint pain and dryness for 3 weeks"},
    )
    assert resp1.status_code == 200
    data1 = resp1.json()
    assert data1["section"] == "chief_complaint"
    assert "chief_complaint" in data1["extracted_data"]

    # Step 2: HPI & Emergency alert check
    resp2 = client.post(
        f"/api/v1/doctor-ai/conversations/{conv_id}/message",
        json={"message": "It started suddenly, and I also felt severe chest pain and breathlessness yesterday"},
    )
    assert resp2.status_code == 200
    data2 = resp2.json()
    assert data2["intent"] == "emergency"
    assert len(data2["risk_flags"]) >= 1

    # Step 3: Ayush profile
    resp3 = client.post(
        f"/api/v1/doctor-ai/conversations/{conv_id}/message",
        json={"message": "I have cold hands and dry skin, prefer warm spicy food, and irregular sleep"},
    )
    assert resp3.status_code == 200
    data3 = resp3.json()
    assert "ayush_assessment" in data3["extracted_data"]
    assert "prakriti_features" in data3["extracted_data"]["ayush_assessment"]
