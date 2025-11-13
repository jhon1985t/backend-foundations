FROM python:3.13-slim

# Usa la forma key=value para evitar warnings
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1 \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8

WORKDIR /app

# Herramientas de compilación (si las necesitas)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc \
 && rm -rf /var/lib/apt/lists/*

# Instala Poetry
RUN pip install --upgrade pip && pip install "poetry==2.2.1"

# Copia solo los manifiestos para aprovechar la caché
COPY pyproject.toml poetry.lock* README.md ./

# Instala dependencias sin instalar el proyecto
RUN poetry install --no-root

# Ahora sí copia el resto del código
COPY . .

EXPOSE 8000

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"]
