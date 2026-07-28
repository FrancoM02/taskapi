"""Tests para los endpoints de autenticación."""


def test_register_success(client):
    """Un usuario nuevo se puede registrar con datos válidos."""
    response = client.post("/auth/register", json={
        "email": "nuevo@example.com",
        "username": "nuevousuario",
        "password": "password123",
    })
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "nuevo@example.com"
    assert data["username"] == "nuevousuario"
    assert "hashed_password" not in data  # Nunca se expone la contraseña


def test_register_duplicate_email(client, registered_user):
    """No se puede registrar con un email ya en uso."""
    response = client.post("/auth/register", json={
        "email": registered_user["email"],
        "username": "otro",
        "password": "password123",
    })
    assert response.status_code == 409
    assert "email" in response.json()["detail"].lower()


def test_register_short_password(client):
    """La contraseña debe tener al menos 8 caracteres."""
    response = client.post("/auth/register", json={
        "email": "x@example.com",
        "username": "usuario",
        "password": "corta",
    })
    assert response.status_code == 422  # Unprocessable Entity (validación Pydantic)


def test_login_success(client, registered_user):
    """Login exitoso devuelve access y refresh tokens."""
    response = client.post("/auth/login", data={
        "username": registered_user["email"],
        "password": registered_user["password"],
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client, registered_user):
    """Login con contraseña incorrecta devuelve 401."""
    response = client.post("/auth/login", data={
        "username": registered_user["email"],
        "password": "contraseña-incorrecta",
    })
    assert response.status_code == 401


def test_get_me_authenticated(client, auth_headers):
    """Un usuario autenticado puede ver su propio perfil."""
    response = client.get("/auth/me", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"


def test_get_me_unauthenticated(client):
    """Sin token, /auth/me devuelve 401."""
    response = client.get("/auth/me")
    assert response.status_code == 401
