from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.auth.routes import router as auth_router
from app.api.routes import router as api_router
from app.users.routes import router as users_router
from app.cache.routes import router as cache_router
from app.error_handlers import (
    handle_http_exception,
    handle_request_validation,
    handle_domain_error,
)
from app.exceptions import DomainError

from app.users.models import User  # noqa: F401 to register the model


def create_app() -> FastAPI:
    app = FastAPI(title="Backend Foundations API", version="1.0.0")
    # Routes
    app.include_router(auth_router)
    app.include_router(api_router)
    app.include_router(users_router)
    app.include_router(cache_router)
    # Global Error Handlers
    app.add_exception_handler(StarletteHTTPException, handle_http_exception)
    app.add_exception_handler(RequestValidationError, handle_request_validation)
    app.add_exception_handler(DomainError, handle_domain_error)
    return app


app = create_app()
