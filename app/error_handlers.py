from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.exceptions import DomainError, ResourceNotFound, ConflictError


def error_envelope(code: str, message: str, status: int, details: dict | None = None):
    return JSONResponse(
        status_code=status,
        content={
            "error": {
                "code": code,
                "message": message,
                "details": details or {},
            }
        },
    )


async def handle_http_exception(request: Request, exc: StarletteHTTPException):
    return error_envelope(
        code=f"HTTP_{exc.status_code}",
        message=exc.detail if isinstance(exc.detail, str) else "HTTP error",
        status=exc.status_code,
        details={
            "method": request.method,
            "url": str(request.url),
            "path": request.url.path,
        },
    )


async def handle_request_validation(request: Request, exc: RequestValidationError):
    # Convert validation errors to JSON-serializable format
    errors = []
    for error in exc.errors():
        error_dict = {
            "loc": error.get("loc", []),
            "msg": error.get("msg", ""),
            "type": error.get("type", ""),
        }
        # Include input if it's serializable
        if "input" in error:
            try:
                error_dict["input"] = str(error["input"])
            except Exception:
                # Ensure we never raise due to non-serializable inputs
                pass
        errors.append(error_dict)

    return error_envelope(
        code="VALIDATION_ERROR",
        message="Request validation error",
        status=422,
        details={"errors": errors, "body": exc.body},
    )


async def handle_domain_error(request: Request, exc: DomainError):
    status = (
        409
        if isinstance(exc, ConflictError)
        else 404 if isinstance(exc, ResourceNotFound) else 400
    )
    return error_envelope(
        code=exc.code,
        message=exc.message,
        status=status,
        details=exc.details | {"path": request.url.path},
    )
