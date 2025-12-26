from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.routes import router as api_router
from app.error_handlers import (
    handle_http_exception,
    handle_request_validation,
    handle_domain_error,
)
from app.exceptions import DomainError
from app.db import engine, Base


def create_app() -> FastAPI:
    app = FastAPI(title="Backend Foundations API", version="1.0.0")
    # Create database tables
    Base.metadata.create_all(bind=engine)
    # Routes
    app.include_router(api_router)
    # Global Error Handlers
    app.add_exception_handler(StarletteHTTPException, handle_http_exception)
    app.add_exception_handler(RequestValidationError, handle_request_validation)
    app.add_exception_handler(DomainError, handle_domain_error)
    return app


app = create_app()
