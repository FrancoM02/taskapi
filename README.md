# Task API

API REST para gestión de tareas personales, construida con FastAPI y PostgreSQL.

## Stack técnico

| Capa | Tecnología | Por qué |
|---|---|---|
| Framework | FastAPI | Moderno, async-ready, documentación automática |
| Base de datos | PostgreSQL | Relacional, robusto, estándar en la industria |
| ORM | SQLAlchemy 2.0 | Type-safe, expresivo, sin magia oculta |
| Autenticación | JWT (access + refresh tokens) | Stateless, escalable, estándar OAuth2 |
| Hashing | bcrypt | Deliberadamente lento, resistente a ataques de fuerza bruta |
| Validación | Pydantic v2 | Validación estricta, rendimiento alto |
| Testing | pytest + SQLite en memoria | Tests aislados, sin dependencias externas |
| Containerización | Docker + docker-compose | Reproducibilidad, facilidad de despliegue |
| CI/CD | GitHub Actions | Automatización, linting y tests en cada PR |

## Ejecutar con Docker (recomendado)

```bash
# 1. Clonar el repositorio
git clone <repo-url>
cd taskapi

# 2. Configurar variables de entorno
cp .env.example .env
# Editar .env con tus valores

# 3. Levantar la app y la base de datos
docker compose up --build

# La API estará disponible en http://localhost:8000
# Documentación interactiva en http://localhost:8000/docs
```

## Ejecutar localmente (sin Docker)

```bash
# 1. Crear entorno virtual
python -m venv venv && source venv/bin/activate

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Configurar variables de entorno
cp .env.example .env
# Editar .env con tu DATABASE_URL local

# 4. Iniciar la app
uvicorn app.main:app --reload
```

## Correr los tests

```bash
pytest tests/ -v
```

## Endpoints principales

| Método | Ruta | Descripción |
|---|---|---|
| POST | `/auth/register` | Registrar usuario |
| POST | `/auth/login` | Login → tokens JWT |
| GET | `/auth/me` | Perfil del usuario autenticado |
| POST | `/tasks/` | Crear tarea |
| GET | `/tasks/` | Listar tareas (con paginación y filtros) |
| GET | `/tasks/{id}` | Obtener tarea por ID |
| PATCH | `/tasks/{id}` | Actualizar tarea parcialmente |
| DELETE | `/tasks/{id}` | Eliminar tarea |

La documentación interactiva completa (Swagger UI) está disponible en `/docs`.

## Decisiones de diseño

**¿Por qué PATCH en lugar de PUT para actualizar?**
PATCH permite actualizaciones parciales — el cliente solo manda los campos que quiere cambiar. PUT reemplaza el recurso completo, lo que requiere mandar todos los campos aunque solo cambie uno.

**¿Por qué 404 cuando un usuario intenta ver la tarea de otro?**
Si devolviéramos 403 (Forbidden), estaríamos revelando que la tarea existe pero no es accesible para ese usuario. Devolver 404 es más seguro: no damos información sobre recursos de otros usuarios.

**¿Por qué access token corto + refresh token largo?**
El access token (30 min) tiene vida corta: si se filtra, el daño es limitado. El refresh token (7 días) permite renovar el access token sin re-loguearse, pero se guarda de forma más segura en el cliente.

## Mejoras futuras

- Migrar `Base.metadata.create_all()` a migraciones con Alembic para mejor control del esquema
- Agregar rate limiting para prevenir abuso de los endpoints de auth
- Implementar logout con blacklist de tokens (Redis)
- Agregar paginación basada en cursor en lugar de offset para mejor rendimiento a escala
- Monitoreo con Prometheus y Grafana
