import grpc

from app.grpc_gen import users_pb2_grpc


_channel = None
_stub = None


def get_user_stub() -> users_pb2_grpc.UserServiceStub:
    global _channel, _stub
    if _stub is None:
        _channel = grpc.insecure_channel("localhost:50051")
        _stub = users_pb2_grpc.UserServiceStub(_channel)
    return _stub
