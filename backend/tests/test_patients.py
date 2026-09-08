from fastapi.testclient import TestClient


def test_get_patient_me(client: TestClient, patient_user):
    _, patient, token = patient_user
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/v1/patients/me", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == patient.id
    assert data["first_name"] == "Ramesh"


def test_update_patient_profile(client: TestClient, patient_user):
    _, patient, token = patient_user
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "address": "Updated Address 123, Bengaluru",
        "emergency_contact": "9998887776",
    }
    response = client.put(f"/api/v1/patients/{patient.id}", json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["address"] == "Updated Address 123, Bengaluru"
    assert data["emergency_contact"] == "9998887776"


def test_cross_patient_unauthorized_access(client: TestClient, patient_user, patient_user_2):
    _, _, token1 = patient_user
    _, patient2, _ = patient_user_2

    # Patient 1 tries to access Patient 2's records
    headers = {"Authorization": f"Bearer {token1}"}
    response = client.get(f"/api/v1/patients/{patient2.id}", headers=headers)
    assert response.status_code == 403


def test_generate_and_link_qr_token(client: TestClient, patient_user, doctor_user):
    _, patient, p_token = patient_user
    _, _, d_token = doctor_user

    # Patient generates short-lived QR token
    p_headers = {"Authorization": f"Bearer {p_token}"}
    qr_res = client.post(f"/api/v1/patients/{patient.id}/qr-token", headers=p_headers)
    assert qr_res.status_code == 200
    qr_payload = qr_res.json()["qr_payload"]
    assert qr_payload.startswith("PCT:v1:")

    # Doctor scans & links patient session using QR payload
    d_headers = {"Authorization": f"Bearer {d_token}"}
    link_res = client.post("/api/v1/patients/qr/link", json={"qr_payload": qr_payload}, headers=d_headers)
    assert link_res.status_code == 200
    assert link_res.json()["id"] == patient.id
