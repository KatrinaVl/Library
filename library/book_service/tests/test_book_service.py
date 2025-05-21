import grpc
from proto import book_service_pb2
from proto import book_service_pb2_grpc

channel = grpc.insecure_channel("book_service:50051")
stub = book_service_pb2_grpc.BookServiceStub(channel)


def test_delete_book():

    response = stub.DeleteBook(
        book_service_pb2.BookRequest(
            id="7e12c25d-e05f-4b2c-b3b4-981b9b891ed2")
    )

    try:
        response_book = stub.GetBook(
            book_service_pb2.BookRequest(
                id="7e12c25d-e05f-4b2c-b3b4-981b9b891ed2")
        )

    except Exception as e:
        print("test is done")


def test_create_book():

    response_book = stub.CreateBook(
        book_service_pb2.CreateBookRequest(
            title="Ruin and Rising _ _",
            author="Leigh Bardugo",
            publish_year=2014,
            isbn="widjfbvjhdqfkgxcvvb",
            count=20,
        )
    )

    assert response_book.id != ""
    assert response_book.title == "Ruin and Rising _ _"
    assert response_book.author == "Leigh Bardugo"
    assert response_book.publish_year == 2014
    assert response_book.isbn == "widjfbvjhdqfkgxcvvb"
    assert response_book.count == 20


def test_update_book():

    response_book = stub.UpdateBook(
        book_service_pb2.UpdateBookRequest(
            id="6bc7f43d-2f4f-459b-8380-5929c16998c2",
            title="Six of Ravens",
            author="Leigh Bardugo",
            publish_year=2015,
            isbn="widjfbhcfxqfvb",
            count=30,
        )
    )

    assert response_book.id == "6bc7f43d-2f4f-459b-8380-5929c16998c2"
    assert response_book.title == "Six of Ravens"
    assert response_book.author == "Leigh Bardugo"
    assert response_book.publish_year == 2015
    assert response_book.isbn == "widjfbhcfxqfvb"
    assert response_book.count == 30


def test_get_book():

    response_book = stub.GetBook(
        book_service_pb2.BookRequest(id="6bc7f43d-2f4f-459b-8380-5929c16998c2")
    )

    assert response_book.id == "6bc7f43d-2f4f-459b-8380-5929c16998c2"
    assert response_book.title == "Six of Ravens"
    assert response_book.author == "Leigh Bardugo"
    assert response_book.publish_year == 2015
    assert response_book.isbn == "widjfbhcfxqfvb"
    assert response_book.count == 30


def test_take_book():

    response_book = stub.GetBook(
        book_service_pb2.BookRequest(id="9acf5987-9b3d-4160-9794-1e6c64bdc60c")
    )

    assert response_book.id == "9acf5987-9b3d-4160-9794-1e6c64bdc60c"
    assert response_book.title == "Siege and Storm"
    assert response_book.author == "Leigh Bardugo"
    assert response_book.publish_year == 2013
    assert response_book.isbn == "widjfbvjhdqfkgvvb"
    assert response_book.count == 20

    response = stub.TakeBook(
        book_service_pb2.BookRequest(id="9acf5987-9b3d-4160-9794-1e6c64bdc60c")
    )

    assert response.success == True

    response_book = stub.GetBook(
        book_service_pb2.BookRequest(id="9acf5987-9b3d-4160-9794-1e6c64bdc60c")
    )

    assert response_book.count == 19


def test_return_book():

    response_book = stub.GetBook(
        book_service_pb2.BookRequest(id="9acf5987-9b3d-4160-9794-1e6c64bdc60c")
    )

    assert response_book.id == "9acf5987-9b3d-4160-9794-1e6c64bdc60c"
    assert response_book.title == "Siege and Storm"
    assert response_book.author == "Leigh Bardugo"
    assert response_book.publish_year == 2013
    assert response_book.isbn == "widjfbvjhdqfkgvvb"
    assert response_book.count == 19

    response = stub.ReturnBook(
        book_service_pb2.BookRequest(id="9acf5987-9b3d-4160-9794-1e6c64bdc60c")
    )

    assert response.success == True

    response_book = stub.GetBook(
        book_service_pb2.BookRequest(id="9acf5987-9b3d-4160-9794-1e6c64bdc60c")
    )

    assert response_book.count == 20


def test_get_books():

    "at this moment I know that in database there are 7 books"

    response = stub.GetBooks(book_service_pb2.PageInfo(per_page=2, page=2))

    assert len(response.books) == 2


def test_get_books_for_list():

    response = stub.GetBooksForList(
        book_service_pb2.BookIdsList(
            book_ids=[
                book_service_pb2.BookRequest(id=b_id)
                for b_id in [
                    "f871c6c2-6002-4587-9896-96fd0cdd8a15",
                    "1ba902da-490d-45bf-9aee-dac9c377d1a5",
                ]
            ]
        )
    )

    assert len(response.books) == 2


def test_update_wrong_book():

    try:
        response_book = stub.UpdateBook(
            book_service_pb2.UpdateBookRequest(
                id="6bc7f43d-2f4f-459b-838adfb8c2",
                title="Six of Ravens",
                author="Leigh Bardugo",
                publish_year=2015,
                isbn="widjfbhcfxqfvb",
                count=30,
            )
        )

    except Exception as e:
        print("test is done")


def test_get_wrong_book():

    try:
        response_book = stub.GetBook(
            book_service_pb2.BookRequest(
                id="6bc7f43d-2f4f-459b-8dafb380-5929c16998c2")
        )

    except Exception as e:
        print("test is done")


def test_delete_wrong_book():

    try:
        response = stub.DeleteBook(
            book_service_pb2.BookRequest(
                id="893699b9-0962-adf4c44-924a-0f3f706cf191")
        )

    except Exception as e:
        print("test is done")


def test_take_wrong_book():

    try:
        response = stub.TakeBook(
            book_service_pb2.BookRequest(
                id="9acf5987-9b3d-4160sd-9794-1e6c64bdc60c")
        )

    except Exception as e:
        print("test is done")


def test_return_wrong_book():

    try:
        response = stub.ReturnBook(
            book_service_pb2.BookRequest(
                id="9acf5987-9erghb3d-4160-9794-1e6c64bdc60c")
        )

    except Exception as e:
        print("test is done")
