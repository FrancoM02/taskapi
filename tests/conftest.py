"""
conftest.py es el archivo de configuración de pytest.
Los fixtures definidos acá están disponibles en todos los archivos de test.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.database import Base, get_db
from app.main import app

# Usamos SQLite en memoria para los tests:
# - No necesita servidor de BD
# - Se crea y destruye en cada sesión de tests
# - Completamente aislado de la BD de desarrollo
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,  # Misma conexión para toda la sesión de tests
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    """
    Fixture de base de datos.
    scope="function": se crea y destruye para cada test.
    Esto garantiza que los tests son independientes entre sí.
    """
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    """
    Fixture del cliente HTTP de prueba.
    Sobreescribe la dependency get_db para usar la BD de tests.
    """
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def registered_user(client):
    """Fixture que registra un usuario y devuelve sus datos."""
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "password123",
    }
    response = client.post("/auth/register", json=user_data)
    assert response.status_code == 201
    return user_data


@pytest.fixture
def auth_headers(client, registered_user):
    """Fixture que devuelve los headers de autenticación listos para usar."""
    response = client.post(
        "/auth/login",
        data={
            "username": registered_user["email"],
            "password": registered_user["password"],
        },
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
