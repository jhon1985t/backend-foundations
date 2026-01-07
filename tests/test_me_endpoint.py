import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_me_endpoint():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # 1. Login first
        login_response = await client.post(
            "/auth/login", data={"username": "user@example.com", "password": "1234"}
        )
        print("\n=== LOGIN ===")
        print(f"Status: {login_response.status_code}")
        print(f"Response: {login_response.json()}")

        assert login_response.status_code == 200
        token = login_response.json()["access_token"]

        # 2. Call /users/me with token
        me_response = await client.get(
            "/users/me", headers={"Authorization": f"Bearer {token}"}
        )
        print("\n=== /users/me ===")
        print(f"Status: {me_response.status_code}")
        print(f"Response: {me_response.json()}")

        assert me_response.status_code == 200


if __name__ == "__main__":
    import asyncio

    asyncio.run(test_me_endpoint())
