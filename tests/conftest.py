import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.main import app

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client():
    def override_get_db():
        session = TestingSessionLocal()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    # Ensure all routers use the override
    for router in app.router.routes:
        if hasattr(router, "dependency_overrides"):  # for APIRouter
            router.dependency_overrides[get_db] = override_get_db
    test_client = TestClient(app)
    yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(client):
    user_data = {"login": "testuser", "password": "testpass123", "repeat_password": "testpass123"}
    response = client.post("/auth", json=user_data)
    return response.json()


@pytest.fixture
def auth_headers(client):
    user_data = {"login": "testuser", "password": "testpass123", "repeat_password": "testpass123"}
    client.post("/auth", json=user_data)

    login_data = {"login": "testuser", "password": "testpass123"}
    response = client.post("/login", json=login_data)
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
