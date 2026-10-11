import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.main import app
from backend.app.core.database import Base, get_db
from backend.app.core.config import settings

from sqlalchemy.pool import StaticPool

TEST_DB_URL = "sqlite:///:memory:"
engine = create_engine(
    TEST_DB_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_registration_success():
    payload = {
        "email": "researcher@clinic.org",
        "password": "Password123!",
        "full_name": "Alice Researcher",
        "role": "USER"
    }
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "researcher@clinic.org"
    assert data["full_name"] == "Alice Researcher"
    assert data["role"] == "USER"
    assert "hashed_password" not in data  # Never leak hashed password in response


def test_registration_duplicate_email():
    payload = {
        "email": "doctor@hospital.org",
        "password": "Password123!",
        "full_name": "Dr. Bob"
    }
    res1 = client.post("/api/auth/register", json=payload)
    assert res1.status_code == 201

    # Attempt registration with duplicate email
    res2 = client.post("/api/auth/register", json=payload)
    assert res2.status_code == 400
    assert "already exists" in res2.json()["detail"]


def test_login_success_and_profile():
    # Register first
    client.post("/api/auth/register", json={
        "email": "doc@medassist.ai",
        "password": "SecurePassword999",
        "full_name": "Dr. Carol",
        "role": "ADMIN"
    })

    # Login
    login_res = client.post("/api/auth/login", json={
        "email": "doc@medassist.ai",
        "password": "SecurePassword999"
    })
    assert login_res.status_code == 200
    token_data = login_res.json()
    assert "access_token" in token_data
    assert token_data["role"] == "ADMIN"
    token = token_data["access_token"]

    # Access protected /api/auth/me
    headers = {"Authorization": f"Bearer {token}"}
    me_res = client.get("/api/auth/me", headers=headers)
    assert me_res.status_code == 200
    me_data = me_res.json()
    assert me_data["email"] == "doc@medassist.ai"
    assert me_data["role"] == "ADMIN"


def test_login_invalid_password():
    client.post("/api/auth/register", json={
        "email": "user@test.org",
        "password": "CorrectPassword123"
    })

    response = client.post("/api/auth/login", json={
        "email": "user@test.org",
        "password": "WrongPassword999"
    })
    assert response.status_code == 401
    assert "Invalid email or password" in response.json()["detail"]


def test_protected_route_without_token():
    response = client.get("/api/auth/me")
    assert response.status_code == 401


def test_protected_route_with_invalid_token():
    headers = {"Authorization": "Bearer invalid.token.payload"}
    response = client.get("/api/auth/me", headers=headers)
    assert response.status_code == 401


def test_rbac_authorization():
    # Register standard USER
    client.post("/api/auth/register", json={
        "email": "nurse@hospital.org",
        "password": "Password1234!",
        "role": "USER"
    })
    user_token = client.post("/api/auth/login", json={
        "email": "nurse@hospital.org",
        "password": "Password1234!"
    }).json()["access_token"]

    # Register ADMIN
    client.post("/api/auth/register", json={
        "email": "chief_officer@hospital.org",
        "password": "Password1234!",
        "role": "ADMIN"
    })
    admin_token = client.post("/api/auth/login", json={
        "email": "chief_officer@hospital.org",
        "password": "Password1234!"
    }).json()["access_token"]

    # Check me profiles reflect roles
    res_user = client.get("/api/auth/me", headers={"Authorization": f"Bearer {user_token}"})
    assert res_user.status_code == 200
    assert res_user.json()["role"] == "USER"

    res_admin = client.get("/api/auth/me", headers={"Authorization": f"Bearer {admin_token}"})
    assert res_admin.status_code == 200
    assert res_admin.json()["role"] == "ADMIN"

