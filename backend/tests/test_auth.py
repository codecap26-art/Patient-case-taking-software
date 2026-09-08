from fastapi.testclient import TestClient


def test_register_patient(client: TestClient):
    payload = {
        "phone": "9811223344",
        "first_name": "Karan",
        "last_name": "Mehta",
        "email": "karan.mehta@test.com",
        "role": "PATIENT",
        "date_of_birth": "1995-04-10",
        "gender": "Male",
        "blood_group": "A+",
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["role"] == "PATIENT"
    assert data["patient_id"] is not None


def test_login_with_password(client: TestClient, patient_user):
    _, _, _ = patient_user
    payload = {
        "phone": "9876543210",
        "password": "patient123",
    }
    response = client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["role"] == "PATIENT"


def test_login_with_otp(client: TestClient, patient_user):
    _, _, _ = patient_user
    payload = {
        "phone": "9876543210",
        "otp": "123456",
    }
    response = client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data


def test_login_invalid_password(client: TestClient, patient_user):
    _, _, _ = patient_user
    payload = {
        "phone": "9876543210",
        "password": "wrong_password_123",
    }
    response = client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 401


def test_get_me(client: TestClient, patient_user):
    _, _, token = patient_user
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["phone"] == "9876543210"
    assert data["role"] == "PATIENT"
