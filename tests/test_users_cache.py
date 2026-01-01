import pytest


@pytest.mark.asyncio
async def test_get_user_caches_response(async_client, redis_client):
    # Create a new user
    user_data = {
        "email": "testuser@example.com",
        "full_name": "Test User",
    }

    response = await async_client.post("/users/", json=user_data)
    assert response.status_code == 201
    user_id = response.json()["id"]

    # First GET request - should fetch from DB and cache it
    response = await async_client.get(f"/users/{user_id}")
    assert response.status_code == 200

    # Check that the user data is now cached in Redis
    cache_key = f"user:{user_id}"
    cached_user = await redis_client.get(cache_key)
    assert cached_user is not None

    # Second GET request - should fetch from cache
    response = await async_client.get(f"/users/{user_id}")
    assert response.status_code == 200
    assert response.json()["email"] == user_data["email"]
    assert response.json()["full_name"] == user_data["full_name"]
