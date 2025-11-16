import pytest


@pytest.mark.asyncio
async def test_validation_error_format(async_client):
    resp = await async_client.post(
        "/items/",
        json={"name": "", "price": -1, "sku": "ABC-123"},
        headers={"x-api-key": "secret-dev-key"},
    )
    assert resp.status_code == 422
    body = resp.json()
    assert body["error"]["code"] == "VALIDATION_ERROR"
    assert "errors" in body["error"]["details"]


@pytest.mark.asyncio
async def test_auth_header_required(async_client):
    payload = {"name": "Mouse", "price": 10.0, "sku": "MOUSE-01"}
    resp = await async_client.post("/items/", json=payload)
    assert resp.status_code == 401
    body = resp.json()
    assert body["error"]["code"] == "HTTP_401"


@pytest.mark.asyncio
async def test_conflict_error(async_client):
    headers = {"x-api-key": "secret-dev-key"}
    payload = {"name": "Teclado", "price": 50.0, "sku": "TECLA-01"}

    r1 = await async_client.post("/items/", json=payload, headers=headers)
    assert r1.status_code == 201

    r2 = await async_client.post("/items/", json=payload, headers=headers)
    assert r2.status_code == 409
    body = r2.json()
    assert body["error"]["code"] == "CONFLICT"
    assert body["error"]["details"]["sku"] == "TECLA-01"
