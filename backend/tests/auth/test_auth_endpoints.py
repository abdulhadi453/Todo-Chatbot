import pytest
import sys
import os
# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from fastapi.testclient import TestClient
from sqlmodel import create_engine, Session, SQLModel
from sqlalchemy.pool import StaticPool
from main import app
from config.database import get_session
from models.todo_model import User


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(bind=engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session):
    def get_session_override():
        yield session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


def test_register_user(client: TestClient):
    """Test user registration endpoint"""
    response = client.post(
        "/auth/register",
        json={
            "email": "test@example.com",
            "password": "testpassword123",
            "name": "Test User"
        }
    )

    assert response.status_code == 201
    data = response.json()
    assert "user_id" in data
    assert data["email"] == "test@example.com"
    assert data["name"] == "Test User"
    assert "access_token" in data
    assert "refresh_token" in data


def test_login_user(client: TestClient):
    """Test user login endpoint"""
    # First register a user
    register_response = client.post(
        "/auth/register",
        json={
            "email": "test2@example.com",
            "password": "testpassword123",
            "name": "Test User 2"
        }
    )
    assert register_response.status_code == 201

    # Then try to login
    response = client.post(
        "/auth/login",
        json={
            "email": "test2@example.com",
            "password": "testpassword123"
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert "user_id" in data
    assert data["email"] == "test2@example.com"
    assert "access_token" in data
    assert "refresh_token" in data


def test_login_invalid_credentials(client: TestClient):
    """Test login with invalid credentials"""
    response = client.post(
        "/auth/login",
        json={
            "email": "nonexistent@example.com",
            "password": "wrongpassword"
        }
    )

    assert response.status_code == 401


def test_get_current_user(client: TestClient):
    """Test getting current user info"""
    # First register a user
    register_response = client.post(
        "/auth/register",
        json={
            "email": "test3@example.com",
            "password": "testpassword123",
            "name": "Test User 3"
        }
    )
    assert register_response.status_code == 201
    register_data = register_response.json()
    token = register_data["access_token"]

    # Then get current user info
    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test3@example.com"
    assert data["name"] == "Test User 3"


def test_register_duplicate_email(client: TestClient):
    """Test registering with duplicate email"""
    # Register first user
    client.post(
        "/auth/register",
        json={
            "email": "duplicate@example.com",
            "password": "testpassword123",
            "name": "Test User 1"
        }
    )

    # Try to register with same email
    response = client.post(
        "/auth/register",
        json={
            "email": "duplicate@example.com",
            "password": "anotherpassword",
            "name": "Test User 2"
        }
    )

    assert response.status_code == 409  # Conflict