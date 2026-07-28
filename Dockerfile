# ── Stage 1: builder ──────────────────────────────────────────────────────────
# Usamos un stage separado para instalar dependencias y luego solo copiamos
# lo necesario. Esto reduce el tamaño final de la imagen.
FROM python:3.12-slim AS builder

WORKDIR /build

# Primero copiamos solo requirements.txt y lo instalamos.
# Docker cachea esta capa: si el código cambia pero no las dependencias,
# no se reinstalan — builds mucho más rápidos.
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# ── Stage 2: runtime ──────────────────────────────────────────────────────────
FROM python:3.12-slim

# Buena práctica: no correr como root dentro del contenedor
RUN useradd --create-home appuser
WORKDIR /home/appuser/app

# Copiamos las dependencias ya instaladas del stage anterior
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copiamos el código de la app
COPY app/ ./app/

# Variables de entorno para Python:
# - PYTHONDONTWRITEBYTECODE: no genera archivos .pyc
# - PYTHONUNBUFFERED: los logs aparecen en tiempo real (importante para Docker)
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
