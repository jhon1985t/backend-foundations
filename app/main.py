from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.routes import router as api_router
from app.users.routes import router as users_router
from app.error_handlers import (
    handle_http_exception,
    handle_request_validation,
    handle_domain_error,
)
from app.exceptions import DomainError
from app.db import engine, Base

from app.users.models import User  # noqa: F401 to register the model


def create_app() -> FastAPI:
    app = FastAPI(title="Backend Foundations API", version="1.0.0")
    # Create database tables (SQLite always works)
    Base.metadata.create_all(bind=engine)
    # Routes
    app.include_router(api_router)
    app.include_router(users_router)
    # Global Error Handlers
    app.add_exception_handler(StarletteHTTPException, handle_http_exception)
    app.add_exception_handler(RequestValidationError, handle_request_validation)
    app.add_exception_handler(DomainError, handle_domain_error)
    return app


app = create_app()
