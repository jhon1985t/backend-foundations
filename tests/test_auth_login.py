import pytest


@pytest.mark.asyncio
async def test_login_success(async_client):
    payload = {
        "email": "user@example.com",
        "full_name": "Login User",
        "password": "1234",
    }

    response = await async_client.post("/users/", json=payload)
    assert response.status_code == 201

    login_response = await async_client.post(
        "/auth/login",
        data={"username": payload["email"], "password": payload["password"]},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    assert login_response.status_code == 200
    body = login_response.json()
    assert "access_token" in body
    assert body.get("token_type") == "bearer"


@pytest.mark.asyncio
async def test_login_failure(async_client):
    payload = {
        "email": "wrong@example.com",
        "full_name": "Wrong User",
        "password": "wrongpassword",
    }

    await async_client.post("/users/", json=payload)

    login_response = await async_client.post(
        "/auth/login",
        data={"username": payload["email"], "password": "incorrect"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    assert login_response.status_code == 401
