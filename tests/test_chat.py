import io
import json
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def get_test_auth_headers(email="chat_tester@medassist.ai"):
    client.post("/api/auth/register", json={
        "email": email,
        "password": "Password123!"
    })
    token = client.post("/api/auth/login", json={
        "email": email,
        "password": "Password123!"
    }).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_sync_chat_flow():
    headers = get_test_auth_headers("chat_sync_user@medassist.ai")

    # 1. Upload sample reference document
    doc_text = "CARDIOLOGY GUIDELINE: Stage 1 hypertension is defined as systolic 130-139 mm Hg."
    files = {"file": ("cardio_guideline.txt", io.BytesIO(doc_text.encode("utf-8")), "text/plain")}
    doc_res = client.post("/api/documents/upload", headers=headers, files=files)
    doc_id = doc_res.json()["id"]

    # 2. Chat query about hypertension
    payload = {
        "message": "What is the systolic range for Stage 1 hypertension?",
        "document_id": doc_id
    }
    chat_res = client.post("/api/chat", headers=headers, json=payload)
    assert chat_res.status_code == 200
    data = chat_res.json()
    assert "conversation_id" in data
    assert "answer" in data
    assert len(data["answer"]) > 20
    assert "Disclaimer" in data["answer"]
    assert "agent" in data
    assert data["processing_time"] >= 0.0

    conv_id = data["conversation_id"]

    # 3. Retrieve conversation history
    conv_res = client.get(f"/api/chat/conversations/{conv_id}", headers=headers)
    assert conv_res.status_code == 200
    conv_data = conv_res.json()
    assert len(conv_data["messages"]) >= 2  # user and assistant
    assert conv_data["messages"][0]["role"] == "user"
    assert conv_data["messages"][1]["role"] == "assistant"

    # 4. List conversations
    list_res = client.get("/api/chat/conversations", headers=headers)
    assert list_res.status_code == 200
    assert len(list_res.json()) >= 1


def test_streaming_chat_sse():
    headers = get_test_auth_headers("chat_stream_user@medassist.ai")

    payload = {
        "message": "Explain clinical management of hypertension."
    }
    response = client.post("/api/chat/stream", headers=headers, json=payload)
    assert response.status_code == 200
    assert "text/event-stream" in response.headers.get("content-type", "")

    # Read SSE events
    events = []
    for line in response.iter_lines():
        if line.startswith("data: "):
            payload_str = line.replace("data: ", "").strip()
            if payload_str:
                events.append(json.loads(payload_str))

    assert len(events) >= 2
    types = [e.get("type") for e in events]
    assert "metadata" in types
    assert "token" in types
    assert "done" in types


def test_delete_conversation():
    headers = get_test_auth_headers("chat_del_user@medassist.ai")

    # Start chat
    chat_res = client.post("/api/chat", headers=headers, json={"message": "Initial test message."})
    conv_id = chat_res.json()["conversation_id"]

    # Delete conversation
    del_res = client.delete(f"/api/chat/conversations/{conv_id}", headers=headers)
    assert del_res.status_code == 200

    # Ensure 404 on subsequent get
    get_res = client.get(f"/api/chat/conversations/{conv_id}", headers=headers)
    assert get_res.status_code == 404
