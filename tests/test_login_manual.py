import pytest


@pytest.mark.asyncio
async def test_login(async_client):
    # Intentar login con usuario existente
    response = await async_client.post(
        "/auth/login", data={"username": "user@example.com", "password": "1234"}
    )
    print(f"\nStatus: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 200


if __name__ == "__main__":
    import asyncio

    asyncio.run(test_login())
