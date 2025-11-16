class DomainError(Exception):
    """Generic Error Of Business."""

    def __init__(
        self, message: str, code: str = "DOMAIN_ERROR", details: dict | None = None
    ):
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(message)


class ResourceNotFound(DomainError):
    def __init__(
        self, message: str = "Resource not found", details: dict | None = None
    ):
        super().__init__(message, code="NOT_FOUND", details=details)


class ConflictError(DomainError):
    def __init__(self, message: str = "Conflict", details: dict | None = None):
        super().__init__(message, code="CONFLICT", details=details)
