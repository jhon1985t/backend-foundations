import pytest


@pytest.mark.asyncio
async def test_create_user(async_client):
    payload = {
        "email": "jhon@test.com",
        "full_name": "Jhon Doe",
        "password": "test1234",
    }
    response = await async_client.post("/users/", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data["id"] >= 1
    assert data["email"] == payload["email"]


@pytest.mark.asyncio
async def test_create_user_conflict(async_client):
    payload = {
        "email": "dup@test.com",
        "full_name": "Duplicate User",
        "password": "test1234",
    }

    # First creation should succeed
    response1 = await async_client.post("/users/", json=payload)
    assert response1.status_code == 201

    # Second creation with the same email should fail
    response2 = await async_client.post("/users/", json=payload)
    assert response2.status_code == 409
    body = response2.json()
    assert body["error"]["code"] == "CONFLICT"
