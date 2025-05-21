from proto import book_service_pb2
from proto import book_service_pb2_grpc
from google.protobuf import empty_pb2

from book_service import database
import uuid
import grpc


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

    def TakeBook(self, request, context):

        taken_book = database.take_book(request.id)
        if not taken_book:
            context.abort(grpc.StatusCode.NOT_FOUND, "Book is not found")

        return book_service_pb2.TakenBook(success=taken_book)

    def ReturnBook(self, request, context):

        returned_book = database.return_book(request.id)
        if not returned_book:
            context.abort(grpc.StatusCode.NOT_FOUND, "Book is not found")

        return book_service_pb2.TakenBook(success=returned_book)

    def GetBooks(self, request, context):

        books = database.get_books()

        start = request.per_page * (request.page - 1)
        end = min(((request.per_page * request.page)), len(books))

        return book_service_pb2.BookList(
            books=[
                book_service_pb2.Book(
                    id=b.id,
                    title=b.title,
                    author=b.author,
                    publish_year=b.publish_year,
                    isbn=b.isbn,
                    count=b.count,
                )
                for b in books[start:end]
            ]
        )

    def GetBooksForList(self, request, context):

        book_ids = []

        for b in request.book_ids:
            book_ids.append(b.id)

        books = database.get_books_for_list(book_ids)

        return book_service_pb2.BookList(
            books=[
                book_service_pb2.Book(
                    id=b.id,
                    title=b.title,
                    author=b.author,
                    publish_year=b.publish_year,
                    isbn=b.isbn,
                    count=b.count,
                )
                for b in books
            ]
        )
