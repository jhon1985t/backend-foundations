from fastapi import APIRouter
from fastapi.responses import JSONResponse
import grpc


from app.grpc.client import get_user_stub
from app.grpc_gen import users_pb2


router = APIRouter(prefix="/grpc", tags=["grpc"])


@router.get("/users/{user_id}")
def grpc_get_user(user_id: int):
    stub = get_user_stub()
    request = users_pb2.GetUserRequest(id=user_id)
    try:
        response = stub.GetUser(request)
        return {
            "id": response.id,
            "email": response.email,
            "full_name": response.full_name,
        }
    except grpc.RpcError as e:
        if e.code() == grpc.StatusCode.NOT_FOUND:
            return JSONResponse(status_code=404, content={"detail": "User not found"})
        return JSONResponse(status_code=502, content={"detail": "Upstream gRPC error"})
