import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_auth_me_endpoint_dev_mode():
    response = client.get("/api/v1/auth/me", headers={"Authorization": "Bearer dev_token"})
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert "email" in data

def test_auth_me_invalid_token_header():
    response = client.get("/api/v1/auth/me", headers={"Authorization": "InvalidHeaderFormat"})
    assert response.status_code == 401
