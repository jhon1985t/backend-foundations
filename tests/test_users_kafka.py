import pytest


@pytest.mark.asyncio
async def test_create_user_emits_kafka_event(async_client, monkeypatch):
    called = {"count": 0, "args": None}

    def fake_emit_user_created(user_id: str, email: str):
        called["count"] += 1
        called["args"] = (user_id, email)

    monkeypatch.setattr("app.users.routes.emit_user_created", fake_emit_user_created)

    payload = {"email": "event@test.com", "full_name": "Event User"}
    response = await async_client.post("/users/", json=payload)

    assert response.status_code == 201
    data = response.json()

    assert called["count"] == 1
    assert called["args"] == (data["id"], data["email"])
