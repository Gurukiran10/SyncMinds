"""
Test configuration and fixtures.
Uses SQLite in-memory database for fast, isolated tests.
"""
import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session

from app.core.database import Base, get_db
from app.main import app
from app.models.user import User
from app.models.meeting import Meeting

# ── In-memory SQLite engine ───────────────────────────────────────────────────

TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def create_tables():
    """Create all tables once per test session."""
    from app.models import user, meeting, transcript, action_item, mention  # noqa: F401
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def db():
    """Provide a fresh database session, rolled back after each test."""
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture()
def client(db):
    """Provide a TestClient with the test database injected."""
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture()
def test_user(db) -> User:
    """Create and return a test user."""
    import bcrypt
    hashed = bcrypt.hashpw(b"testpassword123", bcrypt.gensalt()).decode()
    user = User(
        email="testuser@example.com",
        username="testuser",
        full_name="Test User",
        hashed_password=hashed,
        is_active=True,
        is_verified=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture()
def auth_headers(client, test_user) -> dict:
    """Return Authorization headers for the test user."""
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "testuser", "password": "testpassword123"},
    )
    assert response.status_code == 200, f"Login failed: {response.text}"
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def test_meeting(db, test_user) -> Meeting:
    """Create and return a test meeting."""
    meeting = Meeting(
        title="Test Meeting",
        description="A test meeting",
        organizer_id=test_user.id,
        platform="manual",
        scheduled_start=datetime.utcnow() + timedelta(hours=1),
        scheduled_end=datetime.utcnow() + timedelta(hours=2),
        attendee_ids=[str(test_user.id)],
        status="scheduled",
        transcription_status="pending",
        analysis_status="pending",
    )
    db.add(meeting)
    db.commit()
    db.refresh(meeting)
    return meeting
