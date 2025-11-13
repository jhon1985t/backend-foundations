import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest_asyncio.fixture
async def async_client():
    """Cliente HTTP asíncrono para pruebas de integración.

    Usamos `pytest_asyncio.fixture` para declarar fixtures asíncronas explícitamente.
    Esto evita advertencias/errores en pytest 9 donde los fixtures async deben ser manejados
    por el plugin asyncio.
    """
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client
