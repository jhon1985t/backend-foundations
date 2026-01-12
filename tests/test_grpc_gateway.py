import pytest
import grpc


class FakeResp:
    def __init__(self, id, email, full_name):
        self.id = id
        self.email = email
        self.full_name = full_name


class FakeRpcError(grpc.RpcError):
    def __init__(self, code):
        self._code = code

    def code(self):
        return self._code


@pytest.mark.asyncio
async def test_grpc_get_user_ok(async_client, monkeypatch):
    class FakeStub:
        def GetUser(self, request):
            return FakeResp(
                id=request.id, email="test@example.com", full_name="Test User"
            )

    monkeypatch.setattr("app.grpc.routes.get_user_stub", lambda: FakeStub())

    response = await async_client.get("/grpc/users/1")
    assert response.status_code == 200
    assert response.json()["id"] == 1
    assert response.json()["email"] == "test@example.com"


@pytest.mark.asyncio
async def test_grpc_get_user_not_found(async_client, monkeypatch):
    class FakeStub:
        def GetUser(self, request):
            raise FakeRpcError(grpc.StatusCode.NOT_FOUND)

    monkeypatch.setattr("app.grpc.routes.get_user_stub", lambda: FakeStub())

    response = await async_client.get("/grpc/users/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"
