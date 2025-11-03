import os

import pytest
from fastapi.testclient import TestClient
from moto import mock_s3
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.main import app

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="function")
def aws_mocks():
    """Setup AWS mocks for tests."""
    # Unset S3_ENDPOINT_URL so boto3 uses Moto's endpoint
    old_endpoint = os.environ.pop("S3_ENDPOINT_URL", None)
    # Set AWS credentials before Moto mock
    os.environ["AWS_ACCESS_KEY_ID"] = "test"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "test"
    os.environ["AWS_REGION"] = "us-east-1"
    with mock_s3():
        yield
    if old_endpoint is not None:
        os.environ["S3_ENDPOINT_URL"] = old_endpoint


@pytest.fixture(scope="function")
def ensure_s3_bucket(aws_mocks):
    """Ensure S3 bucket exists in mocked environment."""
    import boto3

    # Ensure AWS credentials are set for Moto S3
    os.environ["AWS_ACCESS_KEY_ID"] = "test"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "test"
    os.environ["AWS_REGION"] = "us-east-1"
    bucket_name = os.getenv("S3_BUCKET_NAME", "test-bucket")
    s3 = boto3.client("s3", region_name=os.environ["AWS_REGION"])
    try:
        s3.create_bucket(Bucket=bucket_name)
    except s3.exceptions.BucketAlreadyExists:
        pass
    except s3.exceptions.BucketAlreadyOwnedByYou:
        pass
    return bucket_name


def get_engine():
    if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
        return create_engine(
            SQLALCHEMY_DATABASE_URL,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
    return create_engine(SQLALCHEMY_DATABASE_URL)


engine = get_engine()
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)


@pytest.fixture(scope="session", autouse=True)
def setup_db():
    # Force AWS credentials for Moto
    os.environ["AWS_ACCESS_KEY_ID"] = "test"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "test"
    os.environ["AWS_REGION"] = "us-east-1"
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(db_session, aws_mocks):
    # Unset S3_ENDPOINT_URL for all test client requests
    old_endpoint = os.environ.pop("S3_ENDPOINT_URL", None)
    # Ensure AWS credentials are set for all requests
    os.environ["AWS_ACCESS_KEY_ID"] = "test"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "test"
    os.environ["AWS_REGION"] = "us-east-1"

    def override_get_db():
        try:
            yield db_session
        finally:
            ...

    from app.api import documents

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[documents.get_s3_service] = (
        lambda: documents.S3Service()
    )
    test_client = TestClient(app)
    yield test_client
    app.dependency_overrides.clear()
    if old_endpoint is not None:
        os.environ["S3_ENDPOINT_URL"] = old_endpoint


@pytest.fixture
def test_user(client):
    user_data = {
        "login": "testuser",
        "password": "testpass123",
        "repeat_password": "testpass123",
    }
    response = client.post("/auth", json=user_data)
    return response.json()


@pytest.fixture
def auth_headers(client):
    user_data = {
        "login": "testuser",
        "password": "testpass123",
        "repeat_password": "testpass123",
    }
    client.post("/auth", json=user_data)

    login_data = {"login": "testuser", "password": "testpass123"}
    response = client.post("/login", json=login_data)
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def test_project(client, auth_headers):
    project_data = {"name": "Test Project"}
    response = client.post(
        "/projects", json=project_data, headers=auth_headers
    )
    assert response.status_code == 201
    return response.json()


@pytest.fixture
def test_document(client, auth_headers, test_project, ensure_s3_bucket):
    import io

    def upload():
        files = [
            ("files", ("file1.txt", io.BytesIO(b"data1"), "text/plain")),
        ]
        response = client.post(
            f"/project/{test_project['id']}/documents",
            files=files,
            headers=auth_headers,
        )
        assert response.status_code == 201
        return response.json()[0]

    return upload()
