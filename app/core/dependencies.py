from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session

from app.core.security import decode_token
from app.db.database import get_db
from app.models.models import User
from app.schemas.schemas import TokenData

# Le dice a FastAPI dónde está el endpoint de login para generar la documentación
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    Dependency que extrae el usuario autenticado del JWT.

    Cualquier endpoint que declare `current_user: User = Depends(get_current_user)`
    queda protegido automáticamente: si el token es inválido o no existe,
    FastAPI devuelve 401 antes de ejecutar el endpoint.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_token(token)

        # Verificamos que sea un access token, no un refresh token
        if payload.get("type") != "access":
            raise credentials_exception

        user_id: int | None = payload.get("sub")
        if user_id is None:
            raise credentials_exception

        token_data = TokenData(user_id=int(user_id))
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.id == token_data.user_id).first()
    if user is None:
        raise credentials_exception
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo"
        )

    return user
