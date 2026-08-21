import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "LawForce" in data["service"]

def test_readiness_endpoint():
    response = client.get("/api/v1/readiness")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"
    assert data["corpus_target"] == 500

def test_sources_listing_endpoint():
    response = client.get("/api/v1/sources?limit=10")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "sources" in data
    assert len(data["sources"]) > 0

def test_chat_query_endpoint():
    response = client.post(
        "/api/v1/chat/query",
        headers={"Authorization": "Bearer dev_token"},
        json={
            "query": "What are the rules for bail under Section 497 CrPC?",
            "jurisdiction": "federal",
            "language": "en"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "chat_id" in data
    assert "answer_markdown" in data
    assert "sources" in data
    assert len(data["sources"]) > 0

def test_admin_stats_endpoint():
    response = client.get("/api/v1/admin/corpus/stats")
    assert response.status_code == 200
    data = response.json()
    assert data["total_documents"] >= 500
    assert data["mandatory_target"] == 500
