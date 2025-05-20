from concurrent import futures

import sys
import os

import grpc
from proto import book_service_pb2
from proto import book_service_pb2_grpc
from book_grpc import BookServiceImpl
import json

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")))


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    book_service_pb2_grpc.add_BookServiceServicer_to_server(
        BookServiceImpl(), server)
    server.add_insecure_port("[::]:50051")
    server.start()
    print("gRPC server started on port 50051")
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
