from fastapi.testclient import TestClient


def test_create_and_view_prescription(client: TestClient, doctor_user, patient_user):
    _, _, d_token = doctor_user
    _, patient, p_token = patient_user
    d_headers = {"Authorization": f"Bearer {d_token}"}
    p_headers = {"Authorization": f"Bearer {p_token}"}

    # 1. Doctor creates prescription
    rx_payload = {
        "patient_id": patient.id,
        "diagnosis_notes": "Acute Viral Pharyngitis",
        "medicines": [
            {
                "name": "Tab. Paracetamol 650mg",
                "dosage": "650 mg",
                "frequency": "1-0-1",
                "duration": "3 Days",
                "instructions": "Take after meals",
            }
        ],
        "general_advice": "Rest and plenty of warm fluids.",
    }
    create_res = client.post("/api/v1/prescriptions", json=rx_payload, headers=d_headers)
    assert create_res.status_code == 201
    rx_data = create_res.json()
    assert rx_data["diagnosis_notes"] == "Acute Viral Pharyngitis"
    assert rx_data["is_active"] is True
    rx_id = rx_data["id"]

    # 2. Patient can view their own prescription
    view_res = client.get(f"/api/v1/prescriptions/{rx_id}", headers=p_headers)
    assert view_res.status_code == 200
    assert view_res.json()["id"] == rx_id

    # 3. Patient listing
    list_res = client.get(f"/api/v1/patients/{patient.id}/prescriptions", headers=p_headers)
    assert list_res.status_code == 200
    assert len(list_res.json()["items"]) >= 1
