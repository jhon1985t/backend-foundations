import pytest


@pytest.mark.asyncio
async def test_me_unauthorized(async_client):
    response = await async_client.get("/users/me")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_me_authorized(async_client):
    payload = {
        "email": "user@example.com",
        "full_name": "Auth User",
        "password": "1234",
    }

    respose = await async_client.post("/users/", json=payload)
    assert respose.status_code == 201

    # Login to get token
    login_response = await async_client.post(
        "/auth/login",
        data={"username": payload["email"], "password": payload["password"]},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert login_response.status_code == 200
    token = login_response.json().get("access_token")

    response_auth = await async_client.get(
        "/users/me", headers={"Authorization": f"Bearer {token}"}
    )

    assert response_auth.status_code == 200
    body = response_auth.json()
    assert body.get("email") == payload["email"]
