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

# Crear tablas en SQLite local (solo la primera vez o cuando local.db no exista)
poetry run python -c "from app.db import engine, Base; from app.users.models import User; Base.metadata.create_all(bind=engine)"

# Servidor (SQLite por defecto)
poetry run uvicorn app.main:app --reload
```

Visita [http://localhost:8000/docs](http://localhost:8000/docs) para ver la documentación interactiva.

**Nota:** Si obtienes error `no such table: users`, ejecuta el comando de creación de tablas antes de levantar el servidor.

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

## 🧪 Probar gRPC (Opcional)

### **Caso 1: Usuario existente (OK)**

**Terminal 1 (Servidor gRPC):**
```powershell
poetry run python app/grpc_server.py
```

**Terminal 2 (Crear usuario vía REST):**
```powershell
poetry run uvicorn app.main:app --host 127.0.0.1 --port 8001
```

**Terminal 3 (Swagger o PowerShell):**
```powershell
# POST /users/ en Swagger (http://127.0.0.1:8001/docs)
# O con PowerShell:
$headers = @{ "x-api-key" = "secret-dev-key"; "Content-Type" = "application/json" }
$body = @{ email = "grpc_demo@example.com"; full_name = "gRPC Demo"; password = "1234" } | ConvertTo-Json
Invoke-RestMethod -Uri http://127.0.0.1:8001/users/ -Method Post -Headers $headers -Body $body
```

**Terminal 4 (Cliente gRPC - buscar ID existente):**
```powershell
poetry run python app/grpc_client_demo.py --id 1
```

**Qué esperar:**
- Terminal 4: `User ID: 1, Email: grpc_demo@example.com, Full Name: gRPC Demo`

---

### **Caso 2: Usuario no existente (NOT_FOUND)**

**Terminal 4 (Cliente gRPC - buscar ID inexistente):**
```powershell
poetry run python app/grpc_client_demo.py --id 9999
```

**Qué esperar:**
- Terminal 4: `RPC failed: code=NOT_FOUND, details=User not found`

---

## � Servicios Opcionales (Redis & Kafka)

### **Redis (Cache)**

Por defecto, los tests que requieren Redis se saltan automáticamente si no está disponible.

**Levantar Redis:**
```powershell
docker compose up redis -d
```

**Verificar conexión:**
- URL: `redis://localhost:6380/0` (puerto 6380 por defecto en docker-compose)
- Test: `poetry run pytest tests/test_users_cache.py -v`

---

### **Kafka (Eventos)**

Por defecto, Kafka está **deshabilitado** (`KAFKA_ENABLED=false`) para evitar errores cuando el broker no está disponible.

**Habilitar Kafka:**
```powershell
# 1. Levantar servicios
docker compose up kafka zookeeper -d

# 2. Habilitar en la app
$env:KAFKA_ENABLED="true"
$env:KAFKA_BOOTSTRAP_SERVERS="localhost:9093"
$env:KAFKA_TOPIC_USER_EVENTS="user-events"

# 3. Levantar servidor
poetry run uvicorn app.main:app --reload
```

**Probar emisión de eventos:**

**Terminal 1 (Consumer):**
```powershell
poetry run python app\kafka\consumer.py
```

**Terminal 2 (Servidor):**
```powershell
$env:KAFKA_ENABLED="true"
poetry run uvicorn app.main:app --reload
```

**Terminal 3 (Crear usuario vía REST):**
```powershell
$headers = @{
    "x-api-key" = "secret-dev-key"
    "Content-Type" = "application/json"
}
$body = @{
    email = "kafka_test@example.com"
    full_name = "Kafka Test"
    password = "1234"
} | ConvertTo-Json

Invoke-RestMethod -Uri http://127.0.0.1:8000/users/ -Method Post -Headers $headers -Body $body
```

**Qué esperar:**
- Terminal 1: verás `Received event: {"event_type": "UserCreated", "user_id": "1", "email": "kafka_test@example.com"}`
- Terminal 2: logs de uvicorn mostrando `POST /users/ 201`
- Terminal 3: respuesta JSON con el usuario creado

---

## 🔧 Comandos Útiles

```powershell
# Levantar PostgreSQL (opcional)
docker compose up db -d

# Levantar Redis + Kafka + ZooKeeper (opcional)
docker compose up redis kafka zookeeper -d

# Migraciones seguras
./scripts/migrate_sqlite.ps1         # SQLite por defecto
./scripts/migrate_postgres.ps1       # PostgreSQL local (puedes pasar -Url "..." para otro destino)

# Servidor en desarrollo
poetry run uvicorn app.main:app --reload

# Tests (19 passed, 1 skipped sin Redis/Kafka)
poetry run pytest -q

# Lint
poetry run ruff check .
poetry run black app tests
pre-commit run --all-files

```
