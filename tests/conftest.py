import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app


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
