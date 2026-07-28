from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


class Base(DeclarativeBase):
    """Clase base de la que heredan todos los modelos."""
    pass


_engine = None
_SessionLocal = None


def get_engine():
    """
    Crea el engine de forma lazy (solo cuando se necesita por primera vez).
    Esto permite que los tests sobreescriban la URL antes de que se cree.
    """
    global _engine
    if _engine is None:
        from app.core.config import settings
        _engine = create_engine(settings.DATABASE_URL)
    return _engine


def get_session_factory():
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=get_engine())
    return _SessionLocal


def get_db():
    """
    Dependency injection para FastAPI.
    Cada endpoint que necesite la BD declara `db: Session = Depends(get_db)`
    y FastAPI se encarga de abrir y cerrar la sesión automáticamente.
    """
    SessionLocal = get_session_factory()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
