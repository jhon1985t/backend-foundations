import pytest


@pytest.mark.asyncio
async def test_me_endpoint(async_client):
    # 1. Create user first
    create_response = await async_client.post(
        "/users/",
        json={
            "email": "user@example.com",
            "full_name": "Test User",
            "password": "1234",
        },
    )
    assert create_response.status_code == 201

    # 2. Login with created user
    login_response = await async_client.post(
        "/auth/login", data={"username": "user@example.com", "password": "1234"}
    )
    print("\n=== LOGIN ===")
    print(f"Status: {login_response.status_code}")
    print(f"Response: {login_response.json()}")

    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    # 3. Call /users/me with token
    me_response = await async_client.get(
        "/users/me", headers={"Authorization": f"Bearer {token}"}
    )
    print("\n=== /users/me ===")
    print(f"Status: {me_response.status_code}")
    print(f"Response: {me_response.json()}")

    assert me_response.status_code == 200
