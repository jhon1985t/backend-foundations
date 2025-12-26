# Backend Foundations Copilot Guide
- **Arquitectura** App factory en [app/main.py](app/main.py#L15-L28) registra un único `api_router` y centraliza 3 handlers globales; sigue este patrón si agregas routers o excepciones para mantener el wiring consistente.
- **Routes** Endpoints en [app/api/routes.py](app/api/routes.py#L6-L43) usando el `router` de módulo; incluye routers adicionales vía `app.include_router` en `create_app`.
- **Auth** Endpoints mutantes dependen de `require_api_key` con header `x-api-key: secret-dev-key` ([app/api/routes.py](app/api/routes.py#L12-L16)); fallas devuelven `HTTP_401`.
- **Data store** Lista en memoria `_fake_db` y contador `_next_id` ([app/api/routes.py](app/api/routes.py#L8-L10)); el estado persiste entre requests/tests, resetea si necesitas aislamiento.
- **Flujo POST /items/** Genera SKU `AUTO-XXXX` si falta y valida unicidad; colisión levanta `ConflictError` ([app/api/routes.py](app/api/routes.py#L23-L43)).
- **Trailing slash** Usa rutas registradas con slash (`/items/`) para evitar 307 que cambian el status (ver [tests/test_api.py](tests/test_api.py#L43-L56)).
- **Validaciones** Pydantic v2 en [app/models.py](app/models.py#L13-L55): SKU regex `^[A-Z0-9-]{6,20}$`, `discount` 0-0.9, precio final siempre >= 1.0 via `model_validator`.
- **Errores y dominio** Envuelve todo en `{error:{code,message,details}}` ([app/error_handlers.py](app/error_handlers.py#L8-L75)); usa `DomainError`/`ConflictError`/`ResourceNotFound` ([app/exceptions.py](app/exceptions.py#L1-L22)) para que el handler asigne 400/404/409 automáticamente.
- **HTTP/validation** `HTTPException` mapea a `HTTP_<status>` con method/url/path; validaciones devuelven `VALIDATION_ERROR` con lista `errors` serializable y `body` crudo ([app/error_handlers.py](app/error_handlers.py#L21-L57)).
- **Buenas prácticas de arquitectura** Mantén lógica de negocio en el router o en nuevas capas pero retornando `DomainError` cuando corresponda; conserva el app factory para pruebas y futura configuración; evita depender directamente de `_fake_db` desde fuera del router para poder reemplazarlo por persistencia real.
- **Patrones de pruebas** Usa `pytest.mark.asyncio` y el fixture `async_client` con `ASGITransport(app=app)` ([tests/conftest.py](tests/conftest.py#L1-L17)) para evitar red; incluye siempre `x-api-key` y la ruta con slash; reinicia `_fake_db`/`_next_id` si un caso necesita estado limpio.
- **Cobertura actual** Pruebas cubren health, creación de item, validaciones, auth y conflicto ([tests/test_api.py](tests/test_api.py#L10-L64), [tests/test_errors.py](tests/test_errors.py#L4-L38)); `test_models.py` e integración están vacíos y listos para extender.
- **Servicios locales**
	- Instala deps: `poetry install` (usa Python 3.13).
	- App en vivo: `poetry run uvicorn app.main:app --reload`.
	- DB opcional: `docker compose up db -d` (no se usa aún en código; es Postgres en 5433).
	- Pruebas: `poetry run pytest -q` o archivos específicos (`poetry run pytest tests/test_api.py -q`).
	- Lint/format: `poetry run ruff check .`, `poetry run black app tests`, `pre-commit run --all-files`.
- **Python path** Pytest agrega el root al `PYTHONPATH` ([pyproject.toml](pyproject.toml#L26-L29)) permitiendo `from app.main import app` sin ajustes.
- **Versionado** Objetivo Python 3.13; FastAPI 0.121 y uvicorn 0.38 fijados en [pyproject.toml](pyproject.toml#L1-L25).
- **Extender rutas** Añade endpoints en [app/api/routes.py](app/api/routes.py#L6-L43) o nuevos módulos y súmalos en `create_app`; registra validaciones/errores coherentes con el envelope para no romper tests.
- **Alineación con tests** Respeta slash, headers y formato de errores; usa `AsyncClient` + `ASGITransport` en nuevos tests en vez de `TestClient` para seguir el estilo existente.
- **Semilla/aislamiento** Usa el fixture `clean_fake_db` de [tests/conftest.py](tests/conftest.py#L5-L29) para limpiar `_fake_db`/`_next_id` en casos que requieran estado limpio; también puedes llamar a `reset_fake_db()` directamente.

---

## 🎯 Roadmap de Evolución

### Estado Actual (Completado)
- ✅ App factory + error handlers centralizados
- ✅ Validaciones Pydantic v2 + dominio de errores
- ✅ Tests async con httpx + ASGITransport
- ✅ CI/CD (GitHub Actions) + linters (ruff, black)
- ✅ Docker + Postgres en compose (no integrado aún)

### Brechas Principales vs Backend Completo
1. **Persistencia:** Postgres definido pero sin ORM/migraciones/repositorios
2. **Arquitectura en capas:** Todo en router, falta services/repositories
3. **Auth:** Solo API key hardcoded, sin JWT/OAuth2/roles
4. **Mensajería:** Sin Kafka/SQS/Celery/eventos de dominio
5. **gRPC:** No existe protobuf ni servicios gRPC
6. **Observabilidad:** Sin logging estructurado/métricas/traces
7. **Testing:** Sin integración con DB real, load tests, contract tests
8. **Config:** Settings hardcoded, sin gestión de entornos/secrets

### Roadmap Sugerido (Orden Pedagógico)

#### **Fase 1: Persistencia (Siguiente paso recomendado)**
- Integrar SQLAlchemy async con Postgres
- Crear modelos ORM + migraciones (Alembic)
- Implementar repositorios (separar de routes)
- Tests con DB real (testcontainers)
- Estructura: `app/db/`, `app/repositories/`, `app/models/` (ORM), `app/schemas/` (DTOs)

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
