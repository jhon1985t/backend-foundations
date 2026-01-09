"""Shared dependencies for FastAPI routes."""


def get_db_factory(session_local):
    """Factory function to create get_db with the correct SessionLocal"""

    def get_db():
        db = session_local()
        try:
            yield db
        finally:
            db.close()

    return get_db


# Import at module level to avoid circular imports
from app.db import SessionLocal  # noqa: E402

get_db = get_db_factory(SessionLocal)
