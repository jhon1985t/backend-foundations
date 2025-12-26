import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.api import routes


@pytest_asyncio.fixture
async def async_client():
    """Cliente HTTP asíncrono para pruebas de integración.

    Se usa `pytest_asyncio.fixture` para declarar fixtures asíncronas y
    `ASGITransport(app=app)` para ejecutar peticiones contra la app ASGI
    en memoria (compatible con httpx >=0.28).
    """
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client


def reset_fake_db():
    """Helper to clear in-memory state between tests."""
    routes._fake_db.clear()
    routes._next_id = 1


@pytest.fixture
def clean_fake_db():
    """Reset `_fake_db`/`_next_id` for tests that need isolation."""
    reset_fake_db()
    yield
    reset_fake_db()
