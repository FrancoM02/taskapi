from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.core.security import create_token, hash_password, verify_password
from app.db.database import get_db
from app.models.models import User
from app.schemas.schemas import Token, UserCreate, UserResponse

router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Registra un nuevo usuario."""
    # Verificar que el email y username no estén en uso
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El email ya está registrado"
        )
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El nombre de usuario ya está en uso"
        )

    user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hash_password(user_data.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """
    Login con email y contraseña.
    Devuelve un access token (30 min) y un refresh token (7 días).
    OAuth2PasswordRequestForm espera los campos 'username' y 'password'
    como form-data (estándar OAuth2).
    """
    # Buscamos por email (usamos el campo 'username' del form para el email)
    user = db.query(User).filter(User.email == form_data.username).first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_token({"sub": str(user.id)}, token_type="access")
    refresh_token = create_token({"sub": str(user.id)}, token_type="refresh")

    return Token(access_token=access_token, refresh_token=refresh_token)


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Devuelve el perfil del usuario autenticado."""
    return current_user
