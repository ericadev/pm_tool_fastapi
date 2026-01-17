import os
import pytest
from urllib.parse import quote
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from dotenv import load_dotenv

from app.main import app
from app.database import Base, get_db

load_dotenv()

# Get individual components from env
db_user = os.getenv("DATABASE_USER", "pm_tool_user")
db_password = os.getenv("DATABASE_PASSWORD", "")
db_host = os.getenv("DATABASE_HOST", "localhost")
db_port = os.getenv("DATABASE_PORT", "5432")

# Encode password for URL safety
encoded_password = quote(db_password, safe="")

# Build test database URL
SQLALCHEMY_TEST_DATABASE_URL = f"postgresql://{db_user}:{encoded_password}@{db_host}:{db_port}/pm_tool_dev"

engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    """Create test database and session."""
    Base.metadata.create_all(bind=engine)
    db_session = TestingSessionLocal()
    yield db_session
    db_session.close()
    # Clean up test data by dropping all tables
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    """Create FastAPI test client with test database."""
    def override_get_db():
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def test_user(client):
    """Create a test user and return user data with token."""
    user_data = {
        "email": "test@example.com",
        "password": "testpassword123",
        "firstName": "Test",
        "lastName": "User"
    }
    response = client.post("/users/", json=user_data)
    assert response.status_code == 200
    user = response.json()

    # Get token by logging in
    login_response = client.post("/users/login", json={
        "email": user_data["email"],
        "password": user_data["password"]
    })
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    return {
        "user": user,
        "credentials": user_data,
        "token": token,
        "headers": {"Authorization": f"Bearer {token}"}
    }
