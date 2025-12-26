# 🧠 Backend Foundations
![CI](https://github.com/TU_USUARIO/backend-foundations/actions/workflows/ci.yml/badge.svg)

Proyecto base para el aprendizaje y desarrollo profesional de **backend con Python**.
Incluye herramientas esenciales para proyectos empresariales modernos (Poetry, pre-commit, pytest, Docker).

---

## 🚀 Requisitos previos

- **Python:** 3.13
- **Poetry:** 1.8+
- **Git:** 2.40+
- **Docker:** 25+

---

## ⚙️ Instalación

```bash
# Clonar el repositorio
git clone https://github.com/tuusuario/backend-foundations.git
cd backend-foundations

# Instalar dependencias
poetry install

# Servidor
poetry run uvicorn app.main:app --reload

Env vars (DB opcional)
----------------------

- Por defecto, la app usa SQLite local (`./local.db`) para evitar dependencias en desarrollo/CI.
- Para usar Postgres, exporta `DATABASE_URL` antes de levantar el server:

```powershell
$env:DATABASE_URL = "postgresql+psycopg://app_user:app_password@localhost:5433/app_db"
docker compose up db -d
poetry run uvicorn app.main:app --reload
```

Tests and notes
================

Pytest configuration
--------------------

- Pytest is configured to include the project root in `PYTHONPATH` via:

  ```toml
  [tool.pytest.ini_options]
  pythonpath = ["."]
  ```

  This allows imports like `from app.main import app` to work when running `pytest`.

httpx tests
-----------

- Tests use `httpx.ASGITransport(app=app)` with `httpx.AsyncClient(transport=...)` so
  requests are executed against the ASGI app in-memory. This is compatible with
  `httpx` >= 0.28 and avoids real network calls during tests.

Trailing slash note
-------------------

- Use registered paths exactly as defined in the app. For example, if the route is
  registered as `@router.post("/items/")`, then calling `POST /items` (without
  trailing slash) will result in a 307 redirect to `/items/` which changes the
  response status and can make tests fail unexpectedly.

Commands
--------
# Server
poetry run uvicorn app.main:app --reload

```powershell
poetry run pytest tests/test_api.py -q
poetry run pytest -q
```

# Lint & format
poetry run ruff check .
poetry run black app tests
pre-commit run --all-files
