import pytest
from sqlmodel import create_engine, SQLModel
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

# Import the app and modules (now available as installed package)
from todo_backend.src.main import app
from todo_backend.src.config.database import get_session
from todo_backend.src.models.todo_model import TodoTask, TodoTaskCreate
from sqlmodel import Session


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
def client_fixture():
    def get_session_override():
        yield session_fixture()

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()