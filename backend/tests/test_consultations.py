from fastapi.testclient import TestClient


def test_create_consultation_and_upload_transcript(client: TestClient, doctor_user, patient_user):
    _, _, d_token = doctor_user
    _, patient, _ = patient_user
    d_headers = {"Authorization": f"Bearer {d_token}"}

    # 1. Doctor starts consultation
    cons_payload = {
        "patient_id": patient.id,
    }
    create_res = client.post("/api/v1/consultations", json=cons_payload, headers=d_headers)
    assert create_res.status_code == 201
    cons_id = create_res.json()["id"]

    # 2. Audio/STT pushes transcript
    transcript_payload = {
        "language": "en",
        "transcript": [
            {"speaker": "doctor", "text": "What symptoms do you have?", "start": 0.0, "end": 2.5},
            {"speaker": "patient", "text": "Throat pain and dry cough for 3 days.", "start": 2.8, "end": 6.1},
        ],
    }
    t_res = client.post(f"/api/v1/consultations/{cons_id}/transcript", json=transcript_payload, headers=d_headers)
    assert t_res.status_code == 200
    assert len(t_res.json()["transcript"]) == 2
    assert t_res.json()["status"] == "RECORDED"
