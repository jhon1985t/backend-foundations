from concurrent import futures

import grpc
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.db import SessionLocal
from app.users.models import User
from app.grpc_gen import users_pb2, users_pb2_grpc


class UserService(users_pb2_grpc.UserServiceServicer):
    def GetUser(self, request, context):
        session: Session | None = None
        try:
            session = SessionLocal()
            user = session.get(User, request.id)
            if user is None:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("User not found")
                return users_pb2.UserResponse()

            return users_pb2.UserResponse(
                id=user.id,
                email=user.email,
                full_name=user.full_name,
            )
        except SQLAlchemyError as exc:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Database error: {exc}")
            return users_pb2.UserResponse()
        finally:
            if session:
                session.close()


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    users_pb2_grpc.add_UserServiceServicer_to_server(UserService(), server)
    # Bind explicitly to localhost to avoid binding issues
    server.add_insecure_port("127.0.0.1:50051")
    server.start()
    print("gRPC server started on port 50051")
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
