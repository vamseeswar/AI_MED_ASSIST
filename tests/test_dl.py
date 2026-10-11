import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from dl.models.classifier_model import get_dl_classifier

client = TestClient(app)


def get_test_auth_headers(email="dl_tester@medassist.ai"):
    client.post("/api/auth/register", json={
        "email": email,
        "password": "Password123!"
    })
    token = client.post("/api/auth/login", json={
        "email": email,
        "password": "Password123!"
    }).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_dl_classifier_direct():
    classifier = get_dl_classifier()
    text = "Comprehensive metabolic panel: Serum sodium 140 mEq/L, Potassium 4.1 mEq/L."
    res = classifier.classify(text)
    assert "label" in res
    assert 0.0 <= res["confidence"] <= 1.0
    assert res["inference_time_ms"] >= 0.0
    assert "model_version" in res


def test_dl_api_endpoint():
    headers = get_test_auth_headers("dl_api_tester@medassist.ai")
    payload = {
        "text": "Patient physical examination reveals clear lungs, normal heart sounds, and no peripheral edema."
    }
    response = client.post("/api/dl/classify", headers=headers, json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "label" in data
    assert "confidence" in data
    assert data["inference_time_ms"] >= 0.0
