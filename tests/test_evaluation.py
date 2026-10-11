"""
Tests for Phase 18 Observability and Phase 19 AI Evaluation.
"""
import pytest
from fastapi.testclient import TestClient

from ai.evaluation.evaluator import RAGEvaluator
from ai.evaluation.runner import run_evaluation, get_latest_evaluation
from backend.app.main import app

client = TestClient(app)


def test_evaluator_retrieval_metrics():
    retrieved = ["doc_1", "doc_2", "doc_3"]
    gt = ["doc_2", "doc_4"]
    
    metrics = RAGEvaluator.evaluate_retrieval(retrieved, gt, k=3)
    assert metrics["hit_rate"] == 1.0
    assert metrics["precision_at_k"] == round(1 / 3, 4)
    assert metrics["recall_at_k"] == 0.5
    assert metrics["mrr"] == 0.5  # doc_2 is at rank 2 -> 1/2


def test_evaluator_context_relevance():
    query = "hypertension blood pressure symptoms"
    contexts = [
        "Hypertension is marked by high blood pressure without early symptoms.",
        "Completely unrelated text about astronomical galaxies and stars."
    ]
    score = RAGEvaluator.evaluate_context_relevance(query, contexts)
    assert score == 0.5


def test_evaluator_citation_correctness():
    retrieved_chunks = [
        {"chunk_id": "c1", "content": "Diabetes involves high blood sugar levels."},
        {"chunk_id": "c2", "content": "Insulin is produced by the pancreas."}
    ]
    citations = [
        {"chunk_id": "c1", "snippet": "blood sugar"},
        {"chunk_id": "fake_c99", "snippet": "hallucinated"}
    ]
    eval_res = RAGEvaluator.evaluate_citation_correctness(citations, retrieved_chunks)
    assert eval_res["citation_count"] == 2
    assert eval_res["valid_citations"] == 1
    assert eval_res["hallucinated_citations"] == 1
    assert eval_res["citation_accuracy"] == 0.5


def test_evaluator_groundedness():
    retrieved = ["Patients with asthma experience airway bronchoconstriction and wheezing."]
    answer = "Patients with asthma have airway bronchoconstriction and wheezing."
    score = RAGEvaluator.evaluate_groundedness(answer, retrieved)
    assert score >= 0.8


def test_evaluation_runner_execution():
    results = run_evaluation()
    assert results["status"] == "COMPLETED"
    assert results["evaluated"] is True
    assert "aggregate_metrics" in results
    assert results["aggregate_metrics"]["total_tokens_consumed"] > 0
    assert "query_details" in results


def get_test_auth_headers(email="eval_admin@medassist.ai"):
    client.post("/api/auth/register", json={
        "email": email,
        "password": "Password123!"
    })
    token = client.post("/api/auth/login", json={
        "email": email,
        "password": "Password123!"
    }).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_admin_api_observability_endpoints():
    auth_headers = get_test_auth_headers("eval_observability@medassist.ai")
    # Test /api/admin/metrics
    resp = client.get("/api/admin/metrics", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"
    assert "counts" in data
    assert "users" in data["counts"]

    # Test /api/admin/audit-logs
    resp_logs = client.get("/api/admin/audit-logs?limit=10", headers=auth_headers)
    assert resp_logs.status_code == 200
    logs_data = resp_logs.json()
    assert "items" in logs_data
    assert "total" in logs_data

    # Test /api/admin/evaluation
    resp_eval = client.get("/api/admin/evaluation", headers=auth_headers)
    assert resp_eval.status_code == 200
    eval_data = resp_eval.json()
    assert eval_data["evaluated"] is True or eval_data["status"] == "Not evaluated yet"
