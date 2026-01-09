import pytest


@pytest.mark.asyncio
async def test_login(async_client):
    # Create user first
    create_response = await async_client.post(
        "/users/",
        json={
            "email": "user@example.com",
            "full_name": "Test User",
            "password": "1234",
        },
    )
    assert create_response.status_code == 201

    # Try login with created user
    response = await async_client.post(
        "/auth/login", data={"username": "user@example.com", "password": "1234"}
    )
    print(f"\nStatus: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 200
