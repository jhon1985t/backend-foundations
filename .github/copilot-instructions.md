# Backend Foundations Copilot Guide
- **Arquitectura** App factory en [app/main.py](app/main.py#L15-L28) registra `api_router` y `users_router`, centraliza 3 handlers globales; sigue este patrón si agregas routers o excepciones para mantener el wiring consistente.
- **Routes** Endpoints en [app/api/routes.py](app/api/routes.py#L6-L43) usando el `router` de módulo; incluye routers adicionales vía `app.include_router` en `create_app`.
- **Auth** Endpoints mutantes dependen de `require_api_key` con header `x-api-key: secret-dev-key` ([app/api/routes.py](app/api/routes.py#L14-L17)); fallas devuelven `HTTP_401`.
- **Data store** Dual: memoria `_fake_db` para items ([app/api/routes.py](app/api/routes.py#L9-L11)) y Postgres para usuarios ([app/users/routes.py](app/users/routes.py#L11-L34)); SQLAlchemy sync con modelo `User` ([app/users/models.py](app/users/models.py#L1-L12)).
- **Flujo POST /items/** Genera SKU `AUTO-XXXX` si falta y valida unicidad; colisión levanta `ConflictError` con `details` dict.
- **Flujo POST /users/** Valida email único en DB; conflicto levanta `ConflictError` con `details={"email": payload.email}` ([app/users/routes.py](app/users/routes.py#L27)).
- **Trailing slash** Usa rutas registradas con slash (`/items/`, `/users/`) para evitar 307 que cambian el status.
- **Validaciones** Pydantic v2 en [app/models.py](app/models.py#L13-L55) y [app/users/schemas.py](app/users/schemas.py#L1-L11): `model_config = {"from_attributes": True}` para ORM, validaciones field-level y model-level.
- **Errores y dominio** Envuelve todo en `{error:{code,message,details}}` ([app/error_handlers.py](app/error_handlers.py#L8-L75)); usa `DomainError`/`ConflictError`/`ResourceNotFound` ([app/exceptions.py](app/exceptions.py#L1-L22)) con parámetro `details` (dict) para que el handler asigne 400/404/409 automáticamente.
- **HTTP/validation** `HTTPException` mapea a `HTTP_<status>` con method/url/path; validaciones devuelven `VALIDATION_ERROR` con lista `errors` serializable y `body` crudo ([app/error_handlers.py](app/error_handlers.py#L21-L57)).
- **Debug endpoint** GET `/debug/db` ([app/api/routes.py](app/api/routes.py#L20-L54)) soporta SQLite y Postgres, devuelve nombre de DB, tablas y URL del engine; útil para verificar conexión.
- **Buenas prácticas de arquitectura** Mantén lógica de negocio en el router o en nuevas capas pero retornando `DomainError` cuando corresponda; conserva el app factory para pruebas y futura configuración.
- **Patrones de pruebas** Usa `@pytest.mark.asyncio` y el fixture `async_client` con `ASGITransport(app=app)` ([tests/conftest.py](tests/conftest.py#L1-L47)) para evitar red; tests que usan DB reciben `db_session` override automáticamente; incluye siempre `x-api-key` y la ruta con slash.
- **Cobertura actual** 10 tests: health, items (4), errores (3), smoke (1), usuarios con DB (2) en [tests/test_users.py](tests/test_users.py#L1-L36); todos pasan con `poetry run pytest -q`.
- **Servicios locales**
	- Instala deps: `poetry install` (usa Python 3.13).
	- App en vivo con Postgres: `$env:DATABASE_URL="postgresql+psycopg://app_user:app_password@localhost:5433/app_db"; poetry run uvicorn app.main:app --reload`.
  - App en vivo con SQLite: `poetry run uvicorn app.main:app --reload` (default, usa `./local.db`).
  - DB Postgres: levanta el servicio con `docker compose up db -d` (puerto 5433).
  - Crear BD de prueba: `docker exec -it $(docker ps -q -f "name=db") psql -U app_user -d postgres -c "CREATE DATABASE app_test_db;"`.
	- Pruebas: `poetry run pytest -q` (10 tests, incluye integración con Postgres en `app_test_db`).
	- Lint/format: `poetry run ruff check .`, `poetry run black app tests`, `pre-commit run --all-files`.
- **Python path** Pytest agrega el root al `PYTHONPATH` ([pyproject.toml](pyproject.toml#L26-L29)) permitiendo `from app.main import app` sin ajustes.
- **Versionado** Objetivo Python 3.13; FastAPI 0.121 y uvicorn 0.38 fijados en [pyproject.toml](pyproject.toml#L1-L25).
- **Config DB** `DATABASE_URL` controla la conexión. Si no está definida, se usa SQLite local (`./local.db`). Tests usan `app_test_db` hardcoded en [tests/conftest.py](tests/conftest.py#L9). Para desarrollo con Postgres: `postgresql+psycopg://app_user:app_password@localhost:5433/app_db`.
- **Extender rutas** Añade endpoints en módulos bajo `app/` y súmalos con `app.include_router` en `create_app`; registra validaciones/errores coherentes con el envelope para no romper tests.
- **Alineación con tests** Respeta slash, headers y formato de errores; usa `AsyncClient` + `ASGITransport` + `@pytest_asyncio.fixture` ([tests/conftest.py](tests/conftest.py#L1-L2)) para fixtures async; convención de nombres `test_*.py` para auto-discovery.

---

## 🎯 Roadmap de Evolución

### Estado Actual (Completado)
- ✅ App factory + error handlers centralizados
- ✅ Validaciones Pydantic v2 + dominio de errores
- ✅ Tests async con httpx + ASGITransport (10 tests pasando)
- ✅ CI/CD (GitHub Actions) + linters (ruff, black)
- ✅ Docker + Postgres en compose (integrado con usuarios)
- ✅ SQLAlchemy sync + modelo User + endpoint POST /users/
- ✅ Endpoint /debug/db compatible con SQLite y Postgres
- ✅ BD de prueba separada (app_test_db) para testing

### Brechas Principales vs Backend Completo
1. **Persistencia:** SQLAlchemy sync básico, falta async/migraciones/repositorios
2. **Arquitectura en capas:** Lógica en routers, falta services/repositories
3. **Auth:** Solo API key hardcoded, sin JWT/OAuth2/roles
4. **Mensajería:** Sin Kafka/SQS/Celery/eventos de dominio
5. **gRPC:** No existe protobuf ni servicios gRPC
6. **Observabilidad:** Sin logging estructurado/métricas/traces
7. **Testing:** Sin load tests, contract tests, mutation testing
8. **Config:** Settings hardcoded, sin gestión de entornos/secrets

### Roadmap Sugerido (Orden Pedagógico)

#### **Fase 1: Persistencia (En progreso)**
- ✅ SQLAlchemy sync integrado con Postgres
- ✅ Modelo User + schemas Pydantic
- ✅ Tests con DB real (testcontainers-style con app_test_db)
- ⏳ Migrar a SQLAlchemy async
- ⏳ Migraciones con Alembic
- ⏳ Implementar repositorios (separar de routes)
- ⏳ Estructura: `app/repositories/`, separar `app/schemas/` de models

#### **Fase 2: Arquitectura en Capas**
- Crear `app/services/` con lógica de negocio
- Dependency injection con FastAPI
- Separar Pydantic schemas de SQLAlchemy models
- Unit of Work pattern para transacciones

#### **Fase 3: Auth Real**
- JWT con FastAPI Security (OAuth2PasswordBearer)
- Endpoints registro/login/refresh token
- RBAC básico con scopes
- Hash passwords con bcrypt

#### **Fase 4: Observabilidad**
- Logging estructurado (structlog con JSON)
- Health checks detallados (DB, servicios externos)
- Métricas Prometheus
- Request ID tracking + correlation

#### **Fase 5: Mensajería Async**
- Kafka producer/consumer (aiokafka)
- Eventos de dominio
- Celery para tareas background
- Dead letter queues

#### **Fase 6: gRPC**
- Protobuf definitions en `protos/`
- Servidor gRPC dual (REST + gRPC)
- Cliente gRPC para microservicios

#### **Fase 7: AWS Integration**
- SQS producer/consumer (aioboto3)
- S3 para archivos
- Secrets Manager
- Deploy a ECS/Lambda

#### **Fase 8: Testing Avanzado**
- Integration tests con testcontainers
- Contract testing (Pact)
- Load testing (Locust/k6)

#### **Fase 9: Kubernetes**
- Manifests (Deployment, Service, ConfigMap)
- Health probes + readiness
- Ingress + cert-manager

### Quick Wins Inmediatos
1. Completar `test_models.py` con validaciones Pydantic
2. Crear flujo E2E en `test_items_flow.py`
3. Versionado API: mover routes a `/api/v1/`
4. Config centralizada con `pydantic-settings`
5. Paginación estándar (`skip`/`limit`)
6. Logging estructurado básico

### Arquitectura Target
```
app/
  ├── api/v1/         # Endpoints versionados
  ├── core/           # config.py, security.py, events.py
  ├── db/             # engine.py, session.py
  ├── models/         # SQLAlchemy ORM
  ├── schemas/        # Pydantic DTOs
  ├── repositories/   # Data access
  ├── services/       # Business logic
  ├── messaging/      # Kafka, SQS
  ├── grpc_services/  # gRPC endpoints
  └── observability/  # logging, metrics
```
