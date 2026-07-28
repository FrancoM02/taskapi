from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.database import get_db
from app.models.models import Task, TaskPriority, TaskStatus, User
from app.schemas.schemas import TaskCreate, TaskListResponse, TaskResponse, TaskUpdate

router = APIRouter(prefix="/tasks", tags=["Tareas"])


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    task_data: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Crea una tarea para el usuario autenticado."""
    task = Task(**task_data.model_dump(), owner_id=current_user.id)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.get("/", response_model=TaskListResponse)
def list_tasks(
    page: int = Query(default=1, ge=1, description="Número de página"),
    per_page: int = Query(default=10, ge=1, le=100, description="Tareas por página"),
    status: TaskStatus | None = Query(default=None, description="Filtrar por estado"),
    priority: TaskPriority | None = Query(default=None, description="Filtrar por prioridad"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Lista las tareas del usuario con paginación y filtros opcionales.
    Ejemplo: GET /tasks?status=pending&priority=high&page=2&per_page=5
    """
    query = db.query(Task).filter(Task.owner_id == current_user.id)

    if status:
        query = query.filter(Task.status == status)
    if priority:
        query = query.filter(Task.priority == priority)

    total = query.count()
    tasks = query.offset((page - 1) * per_page).limit(per_page).all()

    return TaskListResponse(
        tasks=tasks,
        total=total,
        page=page,
        per_page=per_page,
        pages=(total + per_page - 1) // per_page,
    )


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Obtiene una tarea por ID. Solo el dueño puede verla."""
    task = _get_task_or_404(task_id, current_user.id, db)
    return task


@router.patch("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    task_data: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Actualiza parcialmente una tarea (PATCH en lugar de PUT).
    Solo se actualizan los campos que se envíen.
    """
    task = _get_task_or_404(task_id, current_user.id, db)

    # exclude_unset=True: solo los campos que el cliente mandó explícitamente
    update_data = task_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)

    db.commit()
    db.refresh(task)
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Elimina una tarea. Devuelve 204 No Content si fue exitoso."""
    task = _get_task_or_404(task_id, current_user.id, db)
    db.delete(task)
    db.commit()


def _get_task_or_404(task_id: int, user_id: int, db: Session) -> Task:
    """
    Helper privado: busca una tarea que pertenezca al usuario.
    Si no existe O pertenece a otro usuario, devuelve 404.
    (No 403 — no queremos revelar que la tarea existe pero no es tuya.)
    """
    task = db.query(Task).filter(Task.id == task_id, Task.owner_id == user_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tarea {task_id} no encontrada"
        )
    return task
