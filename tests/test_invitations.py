"""Tests for invitation endpoints."""

from datetime import datetime, timedelta

from fastapi import status


def test_share_project_via_email(client, auth_headers, test_project):
    """Test sharing project via email invitation."""
    response = client.get(
        f"/project/{test_project['id']}/share?with_email=invited@example.com",
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "message" in data
    assert "join_link" in data
    assert "invited@example.com" in data["message"]


def test_share_project_unauthorized(client, test_project):
    """Test sharing project without authentication."""
    response = client.get(
        f"/project/{test_project['id']}/share?with_email=test@example.com"
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_share_nonexistent_project(client, auth_headers):
    """Test sharing non-existent project."""
    response = client.get(
        "/project/99999/share?with_email=test@example.com",
        headers=auth_headers,
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_join_project_via_token(
    client, auth_headers, test_project, db_session
):
    """Test joining project via invitation token."""
    from app.models.invite_token import InviteToken

    # Create second user
    user_data = {
        "login": "invitee",
        "email": "invitee@example.com",
        "password": "password123",
        "repeat_password": "password123",
    }
    client.post("/auth", json=user_data)

    # Login as second user
    login_response = client.post(
        "/login", json={"login": "invitee", "password": "password123"}
    )
    invitee_token = login_response.json()["access_token"]
    invitee_headers = {"Authorization": f"Bearer {invitee_token}"}

    # Create invitation token
    invite_token = InviteToken.create_token(
        token="test_token_123",
        project_id=test_project["id"],
        email="invitee@example.com",
        days_valid=7,
    )
    db_session.add(invite_token)
    db_session.commit()

    # Join project
    response = client.post(
        f"/join?token=test_token_123&project_id={test_project['id']}",
        headers=invitee_headers,
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["message"] == "Successfully joined project"
    assert data["project_id"] == test_project["id"]


def test_join_with_invalid_token(client, auth_headers, test_project):
    """Test joining with invalid token."""
    response = client.post(
        f"/join?token=invalid_token&project_id={test_project['id']}",
        headers=auth_headers,
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_join_with_expired_token(
    client, auth_headers, test_project, db_session
):
    """Test joining with expired token."""
    from app.models.invite_token import InviteToken

    # Create expired token
    invite_token = InviteToken(
        token="expired_token",
        project_id=test_project["id"],
        email="testuser@example.com",
        expires_at=datetime.utcnow() - timedelta(days=1),
    )
    db_session.add(invite_token)
    db_session.commit()

    response = client.post(
        f"/join?token=expired_token&project_id={test_project['id']}",
        headers=auth_headers,
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "expired" in response.json()["detail"].lower()


def test_join_with_used_token(
    client, auth_headers, test_project, db_session
):
    """Test joining with already used token."""
    from app.models.invite_token import InviteToken

    # Create used token
    invite_token = InviteToken.create_token(
        token="used_token",
        project_id=test_project["id"],
        email="testuser@example.com",
        days_valid=7,
    )
    invite_token.mark_as_used()
    db_session.add(invite_token)
    db_session.commit()

    response = client.post(
        f"/join?token=used_token&project_id={test_project['id']}",
        headers=auth_headers,
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "already been used" in response.json()["detail"]


def test_join_wrong_email(client, auth_headers, test_project, db_session):
    """Test joining with token sent to different email."""
    from app.models.invite_token import InviteToken

    # Create token for different email
    invite_token = InviteToken.create_token(
        token="wrong_email_token",
        project_id=test_project["id"],
        email="different@example.com",
        days_valid=7,
    )
    db_session.add(invite_token)
    db_session.commit()

    response = client.post(
        f"/join?token=wrong_email_token&project_id={test_project['id']}",
        headers=auth_headers,
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "different email" in response.json()["detail"].lower()


def test_join_already_has_access(
    client, auth_headers, test_project, db_session
):
    """Test joining project user already has access to."""
    from app.models.invite_token import InviteToken

    # Create token for current user
    invite_token = InviteToken.create_token(
        token="duplicate_access_token",
        project_id=test_project["id"],
        email="testuser@example.com",
        days_valid=7,
    )
    db_session.add(invite_token)
    db_session.commit()

    response = client.post(
        f"/join?token=duplicate_access_token&project_id={test_project['id']}",
        headers=auth_headers,
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "already have access" in response.json()["detail"].lower()


def test_get_pending_invitations(
    client, auth_headers, test_project, db_session
):
    """Test getting pending invitations for current user."""
    from app.models.invite_token import InviteToken

    # Create invitation token
    invite_token = InviteToken.create_token(
        token="pending_token",
        project_id=test_project["id"],
        email="testuser@example.com",
        days_valid=7,
    )
    db_session.add(invite_token)
    db_session.commit()

    response = client.get("/invitations", headers=auth_headers)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["token"] == "pending_token"
    assert data[0]["project_id"] == test_project["id"]


def test_get_pending_invitations_empty(client, auth_headers):
    """Test getting pending invitations when none exist."""
    response = client.get("/invitations", headers=auth_headers)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)


def test_get_pending_invitations_unauthorized(client):
    """Test getting invitations without authentication."""
    response = client.get("/invitations")
    assert response.status_code == status.HTTP_403_FORBIDDEN
