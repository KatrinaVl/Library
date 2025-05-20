from proto import book_service_pb2
from proto import book_service_pb2_grpc
from google.protobuf import empty_pb2

from book_service import database
import uuid


class BookServiceImpl(book_service_pb2_grpc.BookServiceServicer):
    def CreateBook(self, request, context):
        data = {
            "title": request.title,
            "author": request.author,
            "publish_year": request.publish_year,
            "isbn": request.isbn,
            "count": request.count,
        }
        book = database.create_book(data)

        response_book = book_service_pb2.Book(
            id=book.id,
            title=book.title,
            author=book.author,
            publish_year=book.publish_year,
            isbn=book.isbn,
            count=book.count,
        )

        return response_book

    def UpdateBook(self, request, context):
        data = {
            "id": request.id,
            "title": request.title,
            "author": request.author,
            "publish_year": request.publish_year,
            "isbn": request.isbn,
            "count": request.count,
        }

        book = database.update_book(data)

        if not book:
            context.abort(grpc.StatusCode.NOT_FOUND, "Book is not found")

        response_book = book_service_pb2.Book(
            id=book.id,
            title=book.title,
            author=book.author,
            publish_year=book.publish_year,
            isbn=book.isbn,
            count=book.count,
        )

        return response_book

    def GetBook(self, request, context):

        book = database.get_book(request.id)

        if not book:
            context.abort(grpc.StatusCode.NOT_FOUND, "Book is not found")

        response_book = book_service_pb2.Book(
            id=book.id,
            title=book.title,
            author=book.author,
            publish_year=book.publish_year,
            isbn=book.isbn,
            count=book.count,
        )

        return response_book

    def DeleteBook(self, request, context):

        book = database.delete_book(request.id)

        if not book:
            context.abort(grpc.StatusCode.NOT_FOUND, "Book is not found")

        return empty_pb2.Empty()
