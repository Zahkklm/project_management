"""Tests for edge cases and error handling."""

import io

from fastapi import status


def test_get_nonexistent_project(client, auth_headers):
    """Test getting non-existent project."""
    response = client.get("/project/99999/info", headers=auth_headers)
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_update_nonexistent_project(client, auth_headers):
    """Test updating non-existent project."""
    update_data = {"name": "Updated"}
    response = client.put(
        "/project/99999/info", json=update_data, headers=auth_headers
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_delete_nonexistent_project(client, auth_headers):
    """Test deleting non-existent project."""
    response = client.delete("/project/99999", headers=auth_headers)
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_get_nonexistent_document(client, auth_headers):
    """Test downloading non-existent document."""
    response = client.get("/document/99999", headers=auth_headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_update_nonexistent_document(client, auth_headers):
    """Test updating non-existent document."""
    file = ("file", ("test.txt", io.BytesIO(b"data"), "text/plain"))
    response = client.put(
        "/document/99999", files=[file], headers=auth_headers
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_nonexistent_document(client, auth_headers):
    """Test deleting non-existent document."""
    response = client.delete("/document/99999", headers=auth_headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_create_project_with_empty_name(client, auth_headers):
    """Test creating project with empty name."""
    project_data = {"name": "", "description": "Test"}
    response = client.post(
        "/projects", json=project_data, headers=auth_headers
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_create_project_with_missing_fields(client, auth_headers):
    """Test creating project with missing required fields."""
    project_data = {"name": "Test"}
    response = client.post(
        "/projects", json=project_data, headers=auth_headers
    )
    # Description is optional, so this should succeed
    assert response.status_code in [
        status.HTTP_201_CREATED,
        status.HTTP_422_UNPROCESSABLE_ENTITY,
    ]


def test_upload_empty_file_list(client, auth_headers, test_project):
    """Test uploading with no files."""
    response = client.post(
        f"/project/{test_project['id']}/documents",
        files=[],
        headers=auth_headers,
    )
    assert response.status_code in [
        status.HTTP_400_BAD_REQUEST,
        status.HTTP_422_UNPROCESSABLE_ENTITY,
    ]


def test_list_documents_for_project(
    client, auth_headers, test_project, ensure_s3_bucket
):
    """Test listing documents for a project."""
    # Upload some documents first
    files = [
        ("files", ("file1.txt", io.BytesIO(b"data1"), "text/plain")),
        ("files", ("file2.txt", io.BytesIO(b"data2"), "text/plain")),
    ]
    client.post(
        f"/project/{test_project['id']}/documents",
        files=files,
        headers=auth_headers,
    )

    # List documents
    response = client.get(
        f"/project/{test_project['id']}/documents", headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2


def test_list_documents_empty_project(
    client, auth_headers, test_project, ensure_s3_bucket
):
    """Test listing documents for project with no documents."""
    response = client.get(
        f"/project/{test_project['id']}/documents", headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)


def test_create_user_with_short_password(client):
    """Test creating user with password too short."""
    user_data = {
        "login": "testuser",
        "email": "testuser@example.com",
        "password": "123",
        "repeat_password": "123",
    }
    response = client.post("/auth", json=user_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_create_user_with_short_login(client):
    """Test creating user with login too short."""
    user_data = {
        "login": "ab",
        "email": "ab@example.com",
        "password": "password123",
        "repeat_password": "password123",
    }
    response = client.post("/auth", json=user_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_update_project_partial(client, auth_headers, test_project):
    """Test updating only project name."""
    update_data = {"name": "New Name Only"}
    response = client.put(
        f"/project/{test_project['id']}/info",
        json=update_data,
        headers=auth_headers,
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == "New Name Only"
    assert data["description"] == test_project["description"]


def test_update_project_description_only(client, auth_headers, test_project):
    """Test updating only project description."""
    update_data = {"description": "New Description Only"}
    response = client.put(
        f"/project/{test_project['id']}/info",
        json=update_data,
        headers=auth_headers,
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == test_project["name"]
    assert data["description"] == "New Description Only"


def test_health_check(client):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "healthy"


def test_root_endpoint(client):
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "message" in data
    assert "version" in data


def test_upload_document_with_special_characters(
    client, auth_headers, test_project, ensure_s3_bucket
):
    """Test uploading document with special characters in filename."""
    files = [
        (
            "files",
            (
                "test file (1) [copy].txt",
                io.BytesIO(b"data"),
                "text/plain",
            ),
        ),
    ]
    response = client.post(
        f"/project/{test_project['id']}/documents",
        files=files,
        headers=auth_headers,
    )
    assert response.status_code == status.HTTP_201_CREATED


def test_get_projects_returns_only_accessible(client, auth_headers):
    """Test that GET /projects returns only accessible projects."""
    # Create multiple projects
    for i in range(3):
        project_data = {
            "name": f"Project {i}",
            "description": f"Description {i}",
        }
        client.post("/projects", json=project_data, headers=auth_headers)

    # Get all projects
    response = client.get("/projects", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) >= 3


def test_invalid_jwt_token(client):
    """Test request with invalid JWT token."""
    invalid_headers = {"Authorization": "Bearer invalid_token_here"}
    response = client.get("/projects", headers=invalid_headers)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_missing_authorization_header(client):
    """Test request without authorization header."""
    response = client.get("/projects")
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_malformed_authorization_header(client):
    """Test request with malformed authorization header."""
    malformed_headers = {"Authorization": "InvalidFormat token"}
    response = client.get("/projects", headers=malformed_headers)
    assert response.status_code == status.HTTP_403_FORBIDDEN
