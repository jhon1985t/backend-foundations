# 🧠 Backend Foundations
![CI](https://github.com/jhon1985t/backend-foundations/actions/workflows/ci.yml/badge.svg)

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

# Servidor (SQLite por defecto)
poetry run uvicorn app.main:app --reload
```

Visita [http://localhost:8000/docs](http://localhost:8000/docs) para ver la documentación interactiva.

---

## 🗄️ Base de Datos

### **SQLite (Default - Recomendado para Desarrollo)**

Por defecto, la app usa **SQLite local** (`./local.db`) para:
- ✅ Sin configuración ni instalación de servicios externos
- ✅ Tests rápidos (in-memory)
- ✅ Compatible con GitHub Actions CI sin setup adicional

**No necesitas hacer nada**, solo corre `poetry run uvicorn app.main:app --reload`.

Para pruebas y CI usamos un archivo dedicado: `./test_db.sqlite` para garantizar aislamiento y diagnósticos consistentes.

---

### **PostgreSQL (Opcional - Para Experimentar)**

Si quieres probar con PostgreSQL (más realista para producción):

**Opción A: Script Automático (Recomendado)**
```powershell
# Setup completo con un comando
.\scripts\setup_postgres.ps1
```

**Opción B: Manual**
```powershell
# 1. Levantar PostgreSQL con Docker
docker compose up db -d

# 2. Crear las tablas (solo la primera vez)
$env:DATABASE_URL="postgresql+psycopg://app_user:app_password@localhost:5433/app_db"
poetry run python -c "from app.db import engine, Base; from app.users.models import User; Base.metadata.create_all(bind=engine)"

# 3. Levantar la app con PostgreSQL
$env:DATABASE_URL="postgresql+psycopg://app_user:app_password@localhost:5433/app_db"
poetry run uvicorn app.main:app --reload
```

**Credenciales PostgreSQL** (configuradas en `docker-compose.yml`):
- Host: `localhost:5433`
- Usuario: `app_user`
- Password: `app_password`
- Base de datos: `app_db`

**pgAdmin** (Opcional): Puedes conectarte con cualquier cliente Postgres a `localhost:5433` para inspeccionar las tablas.

**Nota**: Los tests usan **SQLite en archivo (`./test_db.sqlite`)** para velocidad y aislamiento, y para permitir pasos de diagnóstico en CI.

### **Flujos seguros de migración (evitar errores)**

- **SQLite (default, sin riesgo de apuntar a Postgres):**
  ```powershell
  .\scripts\migrate_sqlite.ps1
  ```
  (limpia `DATABASE_URL`, aplica `alembic upgrade head` sobre `./local.db`).

- **PostgreSQL (solo cuando quieras):**
  ```powershell
  .\scripts\migrate_postgres.ps1
  ```
  (setea `DATABASE_URL` y aplica `alembic upgrade head` al Postgres local por defecto; acepta `-Url` para personalizar).

- **Chequeo rápido de a dónde apuntas:**
  ```powershell
  echo $env:DATABASE_URL   # vacío => SQLite local
  ```

- **Levantar servidor con SQLite (seguro):**
  ```powershell
  Remove-Item Env:DATABASE_URL -ErrorAction SilentlyContinue
  poetry run uvicorn app.main:app --reload
  ```

- **Levantar servidor con Postgres:**
  ```powershell
  $env:DATABASE_URL="postgresql+psycopg://app_user:app_password@localhost:5433/app_db"
  poetry run uvicorn app.main:app --reload
  ```

---

## 🧪 Tests y Desarrollo

### **Ejecutar Tests**

```powershell
# Todos los tests
poetry run pytest -q

# Tests específicos
poetry run pytest tests/test_api.py -v
poetry run pytest tests/test_users.py -v
```

Los tests usan **SQLite en archivo (`./test_db.sqlite`)** automáticamente (rápido y aislado). Se crea/limpia por los fixtures de `pytest` y por el script `scripts/init_test_db.py`.

Usuario sembrado para pruebas:
- Email: `user@example.com`
- Password: `1234`
- Hash: Argon2 via Passlib (`$argon2id$...`)

---

### **Linting y Formato**

```powershell
# Verificar código
poetry run ruff check .

# Formatear código
poetry run black app tests

# Pre-commit hooks (opcional)
pre-commit run --all-files
```

---

## 📝 Notas Técnicas

### CI Pipeline (GitHub Actions)

- Python 3.13, SQLite por defecto.
- Paso de seed: ejecuta `scripts/init_test_db.py` con `DATABASE_URL=sqlite:///./test_db.sqlite`.
- Diagnóstico previo a tests: imprime `DATABASE_URL`, URL del engine, tablas y conteo de usuarios.
- Smoke de Docker: construye la imagen con `--build-arg INSTALL_DEV=true` y corre `pytest` dentro del contenedor.
- Requisitos de sistema en imagen: `librdkafka` (para `confluent-kafka`) y `libffi` (para `argon2-cffi`).

### Auth y Seguridad

- Hash de contraseñas con Argon2 (Passlib), configurado en `app/auth/security.py`.
- Endpoints que mutan requieren header `x-api-key: secret-dev-key`.

### Ejecutar tests en contenedor (local)

```bash
docker build --build-arg INSTALL_DEV=true -t backend-foundations .
docker run --rm -e DATABASE_URL="sqlite:///./test_db.sqlite" backend-foundations poetry run pytest -q
```

### Pytest Configuration

- Pytest incluye el root del proyecto en `PYTHONPATH` vía:

  ```toml
  [tool.pytest.ini_options]
  pythonpath = ["."]
  ```

  Esto permite imports como `from app.main import app` al ejecutar `pytest`.

---

### httpx AsyncClient

- Los tests usan `httpx.ASGITransport(app=app)` con `httpx.AsyncClient` para
  ejecutar requests contra la app ASGI en memoria (sin red real).
  Compatible con `httpx >= 0.28`.

---

### Trailing Slash Note

- Usa las rutas exactamente como están registradas. Si el route es
  `@router.post("/items/")`, llamar `POST /items` (sin trailing slash) resulta
  en un 307 redirect a `/items/` que cambia el status de la respuesta.

---

## 🔧 Comandos Útiles

```powershell
# Levantar PostgreSQL (opcional)
docker compose up db -d

# Levantar Kafka + ZooKeeper
docker compose up kafka zookeeper -d

# Kafka: enviar y consumir un evento de prueba
# En una terminal (consumer)
poetry run python app\kafka\consumer.py
# En otra terminal (producer)
poetry run python -c "from app.kafka.producer import send_user_created_event; send_user_created_event('99','kafka99@example.com')"

# Migraciones seguras
./scripts/migrate_sqlite.ps1         # SQLite por defecto
./scripts/migrate_postgres.ps1       # PostgreSQL local (puedes pasar -Url "..." para otro destino)

# Servidor en desarrollo
poetry run uvicorn app.main:app --reload

# Tests
poetry run pytest -q

# Lint
poetry run ruff check .
poetry run black app tests
pre-commit run --all-files

```
