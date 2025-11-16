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
async def test_create_item_required_fields_only(async_client):
    """Test creating an item with only required fields (name and price)."""
    payload = {"name": "Keyboard", "price": 49.9}
    headers = {"x-api-key": "secret-dev-key"}
    resp = await async_client.post("/items/", json=payload, headers=headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["id"] >= 1
    assert data["name"] == "Keyboard"
    assert data["price"] == 49.9
    assert data["discount"] == 0.0  # default value
    assert data["sku"] is not None  # auto-generated
    assert data["description"] is None  # optional, not provided


@pytest.mark.asyncio
async def test_create_item_all_fields(async_client):
    """Test creating an item with all fields (required + optional)."""
    payload = {
        "name": "Mechanical Keyboard",
        "price": 120.0,
        "discount": 0.15,
        "sku": "KEYB-MK-001",
        "description": "RGB backlit mechanical keyboard with blue switches",
    }
    # NOTE: The route in the app is defined as '/items/' (trailing slash).
    # Posting to '/items' without the slash causes a 307 redirect which
    # would change the status code and test semantics. Use the exact
    # registered path '/items/' to avoid the redirect.
    headers = {"x-api-key": "secret-dev-key"}
    resp = await async_client.post("/items/", json=payload, headers=headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["id"] >= 1
    assert data["name"] == "Mechanical Keyboard"
    assert data["price"] == 120.0
    assert data["discount"] == 0.15
    assert data["sku"] == "KEYB-MK-001"
    assert data["description"] == "RGB backlit mechanical keyboard with blue switches"


@pytest.mark.asyncio
async def test_create_item_validation_error(async_client):
    payload = {"name": "", "price": -5}
    headers = {"x-api-key": "secret-dev-key"}
    resp = await async_client.post("/items/", json=payload, headers=headers)
    assert resp.status_code == 422
