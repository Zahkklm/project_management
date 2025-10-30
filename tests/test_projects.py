import pytest
from fastapi import status


def test_create_project(client, auth_headers):
    project_data = {
        "name": "Test Project",
        "description": "Test Description"
    }
    response = client.post("/projects", json=project_data, headers=auth_headers)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == "Test Project"
    assert data["description"] == "Test Description"
    assert "id" in data


def test_create_project_unauthorized(client):
    project_data = {
        "name": "Test Project",
        "description": "Test Description"
    }
    response = client.post("/projects", json=project_data)
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_get_projects(client, auth_headers):
    project_data = {
        "name": "Test Project",
        "description": "Test Description"
    }
    client.post("/projects", json=project_data, headers=auth_headers)
    
    response = client.get("/projects", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Test Project"


def test_get_project_info(client, auth_headers):
    project_data = {
        "name": "Test Project",
        "description": "Test Description"
    }
    create_response = client.post("/projects", json=project_data, headers=auth_headers)
    project_id = create_response.json()["id"]
    
    response = client.get(f"/project/{project_id}/info", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == "Test Project"


def test_update_project_info(client, auth_headers):
    project_data = {
        "name": "Test Project",
        "description": "Test Description"
    }
    create_response = client.post("/projects", json=project_data, headers=auth_headers)
    project_id = create_response.json()["id"]
    
    update_data = {
        "name": "Updated Project",
        "description": "Updated Description"
    }
    response = client.put(f"/project/{project_id}/info", json=update_data, headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == "Updated Project"
    assert data["description"] == "Updated Description"


def test_delete_project(client, auth_headers):
    project_data = {
        "name": "Test Project",
        "description": "Test Description"
    }
    create_response = client.post("/projects", json=project_data, headers=auth_headers)
    project_id = create_response.json()["id"]
    
    response = client.delete(f"/project/{project_id}", headers=auth_headers)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    get_response = client.get(f"/project/{project_id}/info", headers=auth_headers)
    assert get_response.status_code == status.HTTP_403_FORBIDDEN


def test_invite_user_to_project(client, auth_headers):
    user_data = {
        "login": "inviteduser",
        "password": "password123",
        "repeat_password": "password123"
    }
    client.post("/auth", json=user_data)
    
    project_data = {
        "name": "Test Project",
        "description": "Test Description"
    }
    create_response = client.post("/projects", json=project_data, headers=auth_headers)
    project_id = create_response.json()["id"]
    
    response = client.post(
        f"/project/{project_id}/invite?user=inviteduser",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
