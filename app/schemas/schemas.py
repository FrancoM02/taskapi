from datetime import datetime
from pydantic import BaseModel, EmailStr, Field
from app.models.models import TaskPriority, TaskStatus


# ─────────────────────────────────────────
# USER SCHEMAS
# ─────────────────────────────────────────

class UserCreate(BaseModel):
    """Lo que el cliente manda para registrarse."""
    email: EmailStr
    username: str = Field(min_length=3, max_length=100)
    password: str = Field(min_length=8, description="Mínimo 8 caracteres")


class UserResponse(BaseModel):
    """Lo que la API devuelve sobre un usuario. NUNCA incluye la contraseña."""
    id: int
    email: str
    username: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}  # Permite crear desde un modelo SQLAlchemy


class UserUpdate(BaseModel):
    """Campos opcionales para actualizar el perfil."""
    email: EmailStr | None = None
    username: str | None = Field(default=None, min_length=3, max_length=100)


# ─────────────────────────────────────────
# AUTH SCHEMAS
# ─────────────────────────────────────────

class Token(BaseModel):
    """Respuesta del endpoint de login."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Payload decodificado de un JWT."""
    user_id: int | None = None


# ─────────────────────────────────────────
# TASK SCHEMAS
# ─────────────────────────────────────────

class TaskCreate(BaseModel):
    """Datos para crear una tarea."""
    title: str = Field(min_length=1, max_length=200)
    description: str | None = None
    priority: TaskPriority = TaskPriority.MEDIUM
    due_date: datetime | None = None


class TaskUpdate(BaseModel):
    """Todos los campos son opcionales: se puede actualizar solo lo que se quiera."""
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    status: TaskStatus | None = None
    priority: TaskPriority | None = None
    due_date: datetime | None = None


class TaskResponse(BaseModel):
    """Lo que la API devuelve de una tarea."""
    id: int
    title: str
    description: str | None
    status: TaskStatus
    priority: TaskPriority
    due_date: datetime | None
    created_at: datetime
    updated_at: datetime
    owner_id: int

    model_config = {"from_attributes": True}


class TaskListResponse(BaseModel):
    """Respuesta paginada para el listado de tareas."""
    tasks: list[TaskResponse]
    total: int
    page: int
    per_page: int
    pages: int
