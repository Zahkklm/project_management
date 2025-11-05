"""Tests for access control and permissions."""

from fastapi import status


def test_participant_cannot_delete_project(
    client, auth_headers, test_project
):
    """Test that participant cannot delete project."""
    # Create second user
    user_data = {
        "login": "participant",
        "email": "participant@example.com",
        "password": "password123",
        "repeat_password": "password123",
    }
    client.post("/auth", json=user_data)

    # Invite as participant
    client.post(
        f"/project/{test_project['id']}/invite?user=participant",
        headers=auth_headers,
    )

    # Login as participant
    login_response = client.post(
        "/login", json={"login": "participant", "password": "password123"}
    )
    participant_token = login_response.json()["access_token"]
    participant_headers = {"Authorization": f"Bearer {participant_token}"}

    # Try to delete project
    response = client.delete(
        f"/project/{test_project['id']}", headers=participant_headers
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_participant_can_update_project(client, auth_headers, test_project):
    """Test that participant can update project details."""
    # Create and invite participant
    user_data = {
        "login": "participant2",
        "email": "participant2@example.com",
        "password": "password123",
        "repeat_password": "password123",
    }
    client.post("/auth", json=user_data)
    client.post(
        f"/project/{test_project['id']}/invite?user=participant2",
        headers=auth_headers,
    )

    # Login as participant
    login_response = client.post(
        "/login", json={"login": "participant2", "password": "password123"}
    )
    participant_token = login_response.json()["access_token"]
    participant_headers = {"Authorization": f"Bearer {participant_token}"}

    # Update project
    update_data = {"name": "Updated by Participant"}
    response = client.put(
        f"/project/{test_project['id']}/info",
        json=update_data,
        headers=participant_headers,
    )
    assert response.status_code == status.HTTP_200_OK


def test_participant_cannot_invite_users(client, auth_headers, test_project):
    """Test that participant cannot invite other users."""
    # Create participant
    user_data = {
        "login": "participant3",
        "email": "participant3@example.com",
        "password": "password123",
        "repeat_password": "password123",
    }
    client.post("/auth", json=user_data)
    client.post(
        f"/project/{test_project['id']}/invite?user=participant3",
        headers=auth_headers,
    )

    # Create another user to invite
    user_data2 = {
        "login": "newuser",
        "email": "newuser@example.com",
        "password": "password123",
        "repeat_password": "password123",
    }
    client.post("/auth", json=user_data2)

    # Login as participant
    login_response = client.post(
        "/login", json={"login": "participant3", "password": "password123"}
    )
    participant_token = login_response.json()["access_token"]
    participant_headers = {"Authorization": f"Bearer {participant_token}"}

    # Try to invite user
    response = client.post(
        f"/project/{test_project['id']}/invite?user=newuser",
        headers=participant_headers,
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_non_member_cannot_access_project(
    client, auth_headers, test_project
):
    """Test that non-member cannot access project."""
    # Create another user
    user_data = {
        "login": "outsider",
        "email": "outsider@example.com",
        "password": "password123",
        "repeat_password": "password123",
    }
    client.post("/auth", json=user_data)

    # Login as outsider
    login_response = client.post(
        "/login", json={"login": "outsider", "password": "password123"}
    )
    outsider_token = login_response.json()["access_token"]
    outsider_headers = {"Authorization": f"Bearer {outsider_token}"}

    # Try to access project
    response = client.get(
        f"/project/{test_project['id']}/info", headers=outsider_headers
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_non_member_cannot_access_documents(
    client, auth_headers, test_project, test_document, ensure_s3_bucket
):
    """Test that non-member cannot access project documents."""
    # Create another user
    user_data = {
        "login": "outsider2",
        "email": "outsider2@example.com",
        "password": "password123",
        "repeat_password": "password123",
    }
    client.post("/auth", json=user_data)

    # Login as outsider
    login_response = client.post(
        "/login", json={"login": "outsider2", "password": "password123"}
    )
    outsider_token = login_response.json()["access_token"]
    outsider_headers = {"Authorization": f"Bearer {outsider_token}"}

    # Try to download document
    response = client.get(
        f"/document/{test_document['id']}", headers=outsider_headers
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_owner_can_delete_project(client, auth_headers, test_project):
    """Test that owner can delete project."""
    response = client.delete(
        f"/project/{test_project['id']}", headers=auth_headers
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_invite_nonexistent_user(client, auth_headers, test_project):
    """Test inviting non-existent user."""
    response = client.post(
        f"/project/{test_project['id']}/invite?user=nonexistent",
        headers=auth_headers,
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_invite_user_twice(client, auth_headers, test_project):
    """Test inviting same user twice."""
    # Create user
    user_data = {
        "login": "duplicate_invite",
        "email": "duplicate_invite@example.com",
        "password": "password123",
        "repeat_password": "password123",
    }
    client.post("/auth", json=user_data)

    # First invite
    response1 = client.post(
        f"/project/{test_project['id']}/invite?user=duplicate_invite",
        headers=auth_headers,
    )
    assert response1.status_code == status.HTTP_200_OK

    # Second invite
    response2 = client.post(
        f"/project/{test_project['id']}/invite?user=duplicate_invite",
        headers=auth_headers,
    )
    assert response2.status_code == status.HTTP_400_BAD_REQUEST


def test_participant_can_view_documents(
    client, auth_headers, test_project, ensure_s3_bucket
):
    """Test that participant can view project documents."""
    # Create participant
    user_data = {
        "login": "doc_viewer",
        "email": "doc_viewer@example.com",
        "password": "password123",
        "repeat_password": "password123",
    }
    client.post("/auth", json=user_data)
    client.post(
        f"/project/{test_project['id']}/invite?user=doc_viewer",
        headers=auth_headers,
    )

    # Login as participant
    login_response = client.post(
        "/login", json={"login": "doc_viewer", "password": "password123"}
    )
    participant_token = login_response.json()["access_token"]
    participant_headers = {"Authorization": f"Bearer {participant_token}"}

    # View documents
    response = client.get(
        f"/project/{test_project['id']}/documents",
        headers=participant_headers,
    )
    assert response.status_code == status.HTTP_200_OK


def test_participant_can_upload_documents(
    client, auth_headers, test_project, ensure_s3_bucket
):
    """Test that participant can upload documents."""
    import io

    # Create participant
    user_data = {
        "login": "doc_uploader",
        "email": "doc_uploader@example.com",
        "password": "password123",
        "repeat_password": "password123",
    }
    client.post("/auth", json=user_data)
    client.post(
        f"/project/{test_project['id']}/invite?user=doc_uploader",
        headers=auth_headers,
    )

    # Login as participant
    login_response = client.post(
        "/login", json={"login": "doc_uploader", "password": "password123"}
    )
    participant_token = login_response.json()["access_token"]
    participant_headers = {"Authorization": f"Bearer {participant_token}"}

    # Upload document
    files = [
        ("files", ("test.txt", io.BytesIO(b"test data"), "text/plain")),
    ]
    response = client.post(
        f"/project/{test_project['id']}/documents",
        files=files,
        headers=participant_headers,
    )
    assert response.status_code == status.HTTP_201_CREATED
