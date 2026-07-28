from datetime import datetime, timedelta, timezone
from typing import Literal

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

# CryptContext configura el algoritmo de hashing.
# bcrypt es el estándar actual: es deliberadamente lento para dificultar ataques de fuerza bruta.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Convierte una contraseña en texto plano a su hash bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica si una contraseña coincide con su hash.
    NO se puede revertir el hash — se vuelve a hashear y se compara.
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_token(
    data: dict,
    token_type: Literal["access", "refresh"],
) -> str:
    """
    Crea un JWT firmado.

    El JWT tiene tres partes separadas por puntos:
        header.payload.signature

    - Header: algoritmo usado
    - Payload: datos que queremos guardar (user_id, expiración)
    - Signature: firma digital con SECRET_KEY — garantiza que nadie lo modificó
    """
    to_encode = data.copy()

    if token_type == "access":
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode.update({
        "exp": expire,
        "type": token_type,
    })

    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> dict:
    """
    Decodifica y valida un JWT.
    Lanza JWTError si el token está expirado, fue modificado o es inválido.
    """
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
