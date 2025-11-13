import pytest

# NOTE: httpx API changed in newer versions: AsyncClient no longer accepts an
# 'app' keyword argument directly. Instead we wrap the FastAPI app with
# `httpx.ASGITransport(app=app)` and pass it as `transport=` to AsyncClient.
# This keeps tests running against the in-memory ASGI app without a network
# request and is compatible with httpx >=0.28.


@pytest.mark.asyncio
async def test_health_ok(async_client):
    resp = await async_client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_create_item_ok(async_client):
    payload = {"name": "Keyboard", "price": 49.9, "description": "RGB"}
    # NOTE: The route in the app is defined as '/items/' (trailing slash).
    # Posting to '/items' without the slash causes a 307 redirect which
    # would change the status code and test semantics. Use the exact
    # registered path '/items/' to avoid the redirect.
    resp = await async_client.post("/items/", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert data["id"] >= 1
    assert data["name"] == "Keyboard"
    assert data["price"] == 49.9


@pytest.mark.asyncio
async def test_create_item_validation_error(async_client):
    payload = {"name": "", "price": -5}
    resp = await async_client.post("/items/", json=payload)
    assert resp.status_code == 422
