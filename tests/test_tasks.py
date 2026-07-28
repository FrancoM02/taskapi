"""Tests para los endpoints de tareas."""


def test_create_task(client, auth_headers):
    """Se puede crear una tarea con datos válidos."""
    response = client.post("/tasks/", json={
        "title": "Mi primera tarea",
        "description": "Descripción de la tarea",
        "priority": "high",
    }, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Mi primera tarea"
    assert data["status"] == "pending"  # Estado inicial por defecto
    assert data["priority"] == "high"


def test_create_task_unauthenticated(client):
    """No se puede crear una tarea sin autenticación."""
    response = client.post("/tasks/", json={"title": "Tarea"})
    assert response.status_code == 401


def test_list_tasks_empty(client, auth_headers):
    """Un usuario nuevo no tiene tareas."""
    response = client.get("/tasks/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert data["tasks"] == []


def test_list_tasks_with_filter(client, auth_headers):
    """Se pueden filtrar tareas por estado."""
    # Crear dos tareas con diferentes estados
    client.post("/tasks/", json={"title": "Pendiente"}, headers=auth_headers)
    task_response = client.post("/tasks/", json={"title": "Hecha"}, headers=auth_headers)
    task_id = task_response.json()["id"]
    client.patch(f"/tasks/{task_id}", json={"status": "done"}, headers=auth_headers)

    # Filtrar por pendientes
    response = client.get("/tasks/?status=pending", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["total"] == 1
    assert response.json()["tasks"][0]["title"] == "Pendiente"


def test_update_task(client, auth_headers):
    """Se puede actualizar parcialmente una tarea."""
    create_response = client.post("/tasks/", json={"title": "Original"}, headers=auth_headers)
    task_id = create_response.json()["id"]

    response = client.patch(f"/tasks/{task_id}", json={
        "title": "Actualizada",
        "status": "in_progress",
    }, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Actualizada"
    assert data["status"] == "in_progress"


def test_delete_task(client, auth_headers):
    """Se puede eliminar una tarea propia."""
    create_response = client.post("/tasks/", json={"title": "A eliminar"}, headers=auth_headers)
    task_id = create_response.json()["id"]

    response = client.delete(f"/tasks/{task_id}", headers=auth_headers)
    assert response.status_code == 204

    # Verificar que ya no existe
    get_response = client.get(f"/tasks/{task_id}", headers=auth_headers)
    assert get_response.status_code == 404


def test_cannot_access_other_users_task(client, db):
    """Un usuario no puede ver las tareas de otro usuario."""
    # Registrar dos usuarios
    client.post("/auth/register", json={
        "email": "usuario1@example.com",
        "username": "usuario1",
        "password": "password123",
    })
    client.post("/auth/register", json={
        "email": "usuario2@example.com",
        "username": "usuario2",
        "password": "password123",
    })

    # Login como usuario1 y crear una tarea
    login1 = client.post("/auth/login", data={
        "username": "usuario1@example.com",
        "password": "password123",
    })
    headers1 = {"Authorization": f"Bearer {login1.json()['access_token']}"}
    task_response = client.post("/tasks/", json={"title": "Tarea privada"}, headers=headers1)
    task_id = task_response.json()["id"]

    # Login como usuario2 e intentar ver la tarea de usuario1
    login2 = client.post("/auth/login", data={
        "username": "usuario2@example.com",
        "password": "password123",
    })
    headers2 = {"Authorization": f"Bearer {login2.json()['access_token']}"}
    response = client.get(f"/tasks/{task_id}", headers=headers2)

    # Debe devolver 404, no 403 (no revelar que la tarea existe)
    assert response.status_code == 404
