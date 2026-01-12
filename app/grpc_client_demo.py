import argparse

import grpc
from app.grpc_gen import users_pb2, users_pb2_grpc


def main():
    parser = argparse.ArgumentParser(description="gRPC client demo for UserService")
    parser.add_argument("--id", type=int, default=1, help="User ID to fetch")
    args = parser.parse_args()

    with grpc.insecure_channel("localhost:50051") as channel:
        stub = users_pb2_grpc.UserServiceStub(channel)
        request = users_pb2.GetUserRequest(id=args.id)
        try:
            response = stub.GetUser(request)
            print(
                f"User ID: {response.id}, Email: {response.email}, Full Name: {response.full_name}"
            )
        except grpc.RpcError as exc:
            print(f"RPC failed: code={exc.code().name}, details={exc.details()}")


if __name__ == "__main__":
    main()
