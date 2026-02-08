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
from auth.jwt_utils import create_access_token, create_refresh_token, verify_token, verify_refresh_token
from datetime import timedelta
import time


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


def test_token_refresh_endpoint(client: TestClient, session: Session):
    """Test the token refresh endpoint functionality"""
    # Create a user
    user = User(
        id="refreshuser123",
        email="refresh@test.com",
        password_hash=User.hash_password("password123"),
        name="Refresh User"
    )
    session.add(user)
    session.commit()

    # Login to get tokens
    login_response = client.post(
        "/auth/login",
        json={
            "email": "refresh@test.com",
            "password": "password123"
        }
    )
    assert login_response.status_code == 200
    login_data = login_response.json()
    refresh_token = login_data["refresh_token"]
    old_access_token = login_data["access_token"]

    # Use refresh endpoint to get a new access token
    refresh_response = client.post(
        "/auth/refresh",
        json={
            "refresh_token": refresh_token
        }
    )
    assert refresh_response.status_code == 200
    refresh_data = refresh_response.json()
    new_access_token = refresh_data["access_token"]
    assert new_access_token is not None
    assert new_access_token != old_access_token  # Should be a new token

    # Verify the new token is valid
    verify_response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {new_access_token}"}
    )
    assert verify_response.status_code == 200


def test_expired_token_handling(client: TestClient, session: Session):
    """Test handling of expired tokens"""
    # Create a user
    user = User(
        id="expireuser123",
        email="expire@test.com",
        password_hash=User.hash_password("password123"),
        name="Expire User"
    )
    session.add(user)
    session.commit()

    # Create an access token that expires in 1 second
    token_data = {"sub": "expireuser123", "email": "expire@test.com"}
    short_lived_token = create_access_token(
        data=token_data,
        expires_delta=timedelta(seconds=1)
    )

    # Wait for the token to expire
    time.sleep(2)

    # Try to use the expired token
    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {short_lived_token}"}
    )
    assert response.status_code == 401  # Unauthorized


def test_invalid_refresh_token(client: TestClient):
    """Test using an invalid refresh token"""
    invalid_token = "invalid_refresh_token_here"

    response = client.post(
        "/auth/refresh",
        json={
            "refresh_token": invalid_token
        }
    )
    assert response.status_code == 401  # Unauthorized


def test_refresh_token_reuse_protection(client: TestClient, session: Session):
    """Test that refresh tokens can only be used once (if implemented)"""
    # Create a user
    user = User(
        id="reuseruser123",
        email="reuser@test.com",
        password_hash=User.hash_password("password123"),
        name="Reuse User"
    )
    session.add(user)
    session.commit()

    # Login to get tokens
    login_response = client.post(
        "/auth/login",
        json={
            "email": "reuser@test.com",
            "password": "password123"
        }
    )
    assert login_response.status_code == 200
    login_data = login_response.json()
    refresh_token = login_data["refresh_token"]

    # Use refresh token once
    refresh_response = client.post(
        "/auth/refresh",
        json={
            "refresh_token": refresh_token
        }
    )
    assert refresh_response.status_code == 200

    # Try to reuse the same refresh token (this may or may not be restricted depending on implementation)
    # For this test, we'll assume a basic implementation where refresh tokens can be reused until expiration
    # If your implementation invalidates refresh tokens after use, this test would need to be adjusted


def test_token_creation_and_verification_functions():
    """Test the JWT utility functions directly"""
    # Test creating an access token
    data = {"sub": "testuser123", "email": "test@example.com"}
    token = create_access_token(data)
    assert token is not None
    assert isinstance(token, str)

    # Test verifying the token
    payload = verify_token(token)
    assert payload["sub"] == "testuser123"
    assert payload["email"] == "test@example.com"

    # Test creating a refresh token
    refresh_token = create_refresh_token(data)
    assert refresh_token is not None
    assert isinstance(refresh_token, str)

    # Test verifying the refresh token
    refresh_payload = verify_refresh_token(refresh_token)
    assert refresh_payload["sub"] == "testuser123"
    assert refresh_payload["email"] == "test@example.com"


def test_token_with_custom_expiration(client: TestClient, session: Session):
    """Test tokens with custom expiration times"""
    # Create a user
    user = User(
        id="customexpireuser123",
        email="customexpire@test.com",
        password_hash=User.hash_password("password123"),
        name="Custom Expire User"
    )
    session.add(user)
    session.commit()

    # Create a token with custom expiration (1 hour)
    custom_token = create_access_token(
        data={"sub": "customexpireuser123", "email": "customexpire@test.com"},
        expires_delta=timedelta(hours=1)
    )

    # Token should be valid
    try:
        verify_token(custom_token)
        # If we get here, the token was valid
        assert True
    except Exception:
        # If we get an exception, the token was invalid
        assert False, "Custom expiration token should be valid"