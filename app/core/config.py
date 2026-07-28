from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Base de datos
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/taskapi"

    # JWT
    SECRET_KEY: str = "cambia-esto-en-produccion-por-una-clave-larga-y-aleatoria"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # App
    PROJECT_NAME: str = "Task API"
    VERSION: str = "1.0.0"

    class Config:
        env_file = ".env"  # Lee variables desde un archivo .env


settings = Settings()
