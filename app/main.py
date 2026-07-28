from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routers import auth, tasks

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="""
    API REST para gestión de tareas personales.

    ## Funcionalidades
    - **Registro y autenticación** con JWT (access + refresh tokens)
    - **CRUD completo** de tareas con estados y prioridades
    - **Paginación y filtros** en el listado de tareas
    - **Aislamiento de datos**: cada usuario solo ve sus propias tareas
    """,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(tasks.router)


@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "version": settings.VERSION}


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "healthy"}
