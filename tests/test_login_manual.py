import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_login():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Intentar login con usuario existente
        response = await client.post(
            "/auth/login", data={"username": "user@example.com", "password": "1234"}
        )
        print(f"\nStatus: {response.status_code}")
        print(f"Response: {response.json()}")
        assert response.status_code == 200


if __name__ == "__main__":
    import asyncio

    asyncio.run(test_login())
