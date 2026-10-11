import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from ml.inference.classifier import get_ml_classifier

client = TestClient(app)


def get_test_auth_headers(email="ml_tester@medassist.ai"):
    client.post("/api/auth/register", json={
        "email": email,
        "password": "Password123!"
    })
    token = client.post("/api/auth/login", json={
        "email": email,
        "password": "Password123!"
    }).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_ml_classifier_direct():
    classifier = get_ml_classifier()

    # Lab sample
    lab_text = "Complete blood count: Hemoglobin 13.5 g/dL, Platelets 220,000, WBC 5.8."
    res_lab = classifier.classify(lab_text)
    assert res_lab["category"] == "laboratory_report"
    assert res_lab["confidence"] > 0.0
    assert res_lab["inference_time_ms"] >= 0.0
    assert "model_version" in res_lab

    # Insurance sample
    ins_text = "Health insurance claim form CMS-1500. Policy ID POL-99212. Copay amount $20.00."
    res_ins = classifier.classify(ins_text)
    assert res_ins["category"] == "insurance_document"


def test_ml_api_endpoint():
    headers = get_test_auth_headers("ml_api_tester@medassist.ai")
    payload = {
        "text": "Abstract: Randomized double-blind clinical trial evaluating monoclonal antibodies in cardiology. Peer-reviewed journal DOI 10.1016."
    }
    response = client.post("/api/ml/classify-document", headers=headers, json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["category"] in ["medical_research", "clinical_report"]
    assert 0.0 < data["confidence"] <= 1.0
    assert data["inference_time_ms"] >= 0.0
    assert "model_version" in data
