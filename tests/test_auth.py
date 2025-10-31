from fastapi import status


def test_create_user(client):
    user_data = {"login": "newuser", "password": "password123", "repeat_password": "password123"}
    response = client.post("/auth", json=user_data)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["login"] == "newuser"
    assert "id" in data


def test_create_user_duplicate(client, test_user):
    user_data = {"login": "testuser", "password": "password123", "repeat_password": "password123"}
    response = client.post("/auth", json=user_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_create_user_password_mismatch(client):
    user_data = {"login": "newuser", "password": "password123", "repeat_password": "different123"}
    response = client.post("/auth", json=user_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_login_success(client, test_user):
    login_data = {"login": "testuser", "password": "testpass123"}
    response = client.post("/login", json=login_data)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client, test_user):
    login_data = {"login": "testuser", "password": "wrongpassword"}
    response = client.post("/login", json=login_data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_login_nonexistent_user(client):
    login_data = {"login": "nonexistent", "password": "password123"}
    response = client.post("/login", json=login_data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
