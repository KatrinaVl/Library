from datetime import datetime, timedelta

import jwt
import hashlib
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from google.protobuf.json_format import MessageToDict

from . import database, model
import grpc
from proto import book_service_pb2
from proto import book_service_pb2_grpc

app = FastAPI()

channel = grpc.insecure_channel("book_service:50051")
stub = book_service_pb2_grpc.BookServiceStub(channel)


SECRET_KEY = "Library__"
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def create_token(data, expires_time=timedelta(minutes=30)):
    """
    Create token
    """

    to_encode = data.copy()
    expire = datetime.utcnow() + expires_time
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str = Depends(oauth2_scheme)):
    """
    Decode token
    """

    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return decoded
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


@app.post("/register")
def register(request: model.Librarian):
    """
    Register of librarian
    """
    try:
        hash_password = hashlib.sha256(request.password.encode())
        hex_dig = hash_password.hexdigest()

        database.create_librarian({
            "email": request.email,
            "password": hex_dig})

        return JSONResponse(
            content={"message": "registration is successful"}, status_code=201
        )
    except Exception as e:
        return JSONResponse(content={"message": str(e)}, status_code=500)


@app.post("/login")
def login(request: model.Librarian):
    """
    Login of librarian
    """

    try:
        librarian = database.find_librarian(
            {"email": request.email, "password": request.password}
        )

        hash_password = hashlib.sha256(request.password.encode())
        hex_dig = hash_password.hexdigest()

        if hex_dig != librarian.password:
            return JSONResponse(
                content={"message": "wrong password"},
                status_code=401)

        token = create_token({"librarian_id": librarian.id})

        return JSONResponse(content={"token": token}, status_code=201)

    except Exception as e:
        return JSONResponse(content={"message": str(e)}, status_code=500)


@app.post("/register_book")
def register_book(
        request: model.BookInfo,
        token_body: dict = Depends(decode_token)):

    """
    Register new book
    """

    try:

        librarian = database.find_librarian_id(token_body["librarian_id"])
        if not librarian:
            return JSONResponse(
                content={"message": "Invalid token"},
                status_code=401)

        response_book = stub.CreateBook(
            book_service_pb2.CreateBookRequest(**request.dict(exclude={"id"}))
        )

        response = {
            "message": "register information is successful",
            "book": MessageToDict(response_book),
        }

        return JSONResponse(content=response, status_code=201)
    except Exception as e:
        return JSONResponse(content={"message": str(e)}, status_code=500)


@app.post("/update_book")
def update_book(
        request: model.BookInfo, token_body: dict = Depends(decode_token)):

    """
    Update information in book
    """

    try:

        librarian = database.find_librarian_id(token_body["librarian_id"])
        if not librarian:
            return JSONResponse(
                content={"message": "Invalid token"},
                status_code=401)

        response_book = stub.UpdateBook(
            book_service_pb2.UpdateBookRequest(**request.dict())
        )

        response = {
            "message": "changing information is successful",
            "book": MessageToDict(response_book),
        }
        return JSONResponse(content=response, status_code=200)
    except Exception as e:
        return JSONResponse(content={"message": str(e)}, status_code=500)


@app.get("/get_book/{book_id}")
def get_book(book_id: str, token_body: dict = Depends(decode_token)):

    """
    Get book with book_id
    """

    try:

        librarian = database.find_librarian_id(token_body["librarian_id"])
        if not librarian:
            return JSONResponse(
                content={"message": "Invalid token"},
                status_code=401)

        response_book = stub.GetBook(
            book_service_pb2.BookRequest(id=book_id))

        response = {"message": "book is found",
                    "book": MessageToDict(response_book)}

        return JSONResponse(content=response, status_code=200)
    except Exception as e:
        return JSONResponse(content={"message": str(e)}, status_code=500)


@app.delete("/delete_book/{book_id}")
def delete_book(book_id: str, token_body: dict = Depends(decode_token)):

    """
    Delete book with book_id
    """

    try:

        librarian = database.find_librarian_id(token_body["librarian_id"])
        if not librarian:
            return JSONResponse(
                content={"message": "Invalid token"},
                status_code=401)

        response = {"message": "book is deleted"}
        return JSONResponse(content=response, status_code=200)
    except Exception as e:
        return JSONResponse(content={"message": str(e)}, status_code=500)


@app.post("/add_reader")
def add_reader(reader: model.Reader, token_body: dict = Depends(decode_token)):

    """
    Add new reader
    """

    try:

        librarian = database.find_librarian_id(token_body["librarian_id"])
        if not librarian:
            return JSONResponse(
                content={"message": "Invalid token"},
                status_code=401)

        database.add_reader(reader)
        response = {"message": "reader is added"}
        return JSONResponse(content=response, status_code=201)

    except Exception as e:
        return JSONResponse(content={"message": str(e)}, status_code=500)


@app.post("/update_reader/{reader_id}")
def update_reader(
    reader_id: str, reader: model.Reader,
    token_body: dict = Depends(decode_token)
):

    """
    Update information about reader
    """

    try:

        librarian = database.find_librarian_id(token_body["librarian_id"])
        if not librarian:
            return JSONResponse(
                content={"message": "Invalid token"},
                status_code=401)

        new_reader = database.update_reader(reader, reader_id)
        response = {
            "message": "information about reader has changed",
            "reader": {"name": new_reader.name, "email": new_reader.email},
        }
        return JSONResponse(content=response, status_code=200)

    except Exception as e:
        return JSONResponse(content={"message": str(e)}, status_code=500)


@app.get("/get_reader/{reader_id}")
def get_reader(reader_id: str, token_body: dict = Depends(decode_token)):

    """
    Get reader with reader_id
    """

    try:

        librarian = database.find_librarian_id(token_body["librarian_id"])
        if not librarian:
            return JSONResponse(
                content={"message": "Invalid token"},
                status_code=401)

        reader = database.get_reader(reader_id)

        response = {
            "message": "reader is found",
            "reader": {"name": reader.name, "email": reader.email},
        }
        return JSONResponse(content=response, status_code=200)
    except Exception as e:
        return JSONResponse(content={"message": str(e)}, status_code=500)


@app.delete("/delete_reader/{reader_id}")
def delete_reader(reader_id: str, token_body: dict = Depends(decode_token)):

    """
    Delete reader with reader_id
    """

    try:

        librarian = database.find_librarian_id(token_body["librarian_id"])
        if not librarian:
            return JSONResponse(
                content={"message": "Invalid token"},
                status_code=401)

        reader = database.delete_reader(reader_id)

        if not reader:
            return JSONResponse(
                content={"message": "Reader is not found"}, status_code=401
            )

        response = {
            "message": "reader is deleted",
            "reader": {"name": reader.name, "email": reader.email},
        }
        return JSONResponse(content=response, status_code=200)
    except Exception as e:
        return JSONResponse(content={"message": str(e)}, status_code=500)


@app.post("/give_book")
def give_book(
        request: model.GiveRequest,
        token_body: dict = Depends(decode_token)):

    """
    Give book with book_id to reader with reader_id
    """

    try:

        librarian = database.find_librarian_id(token_body["librarian_id"])
        if not librarian:
            return JSONResponse(
                content={"message": "Invalid token"},
                status_code=401)

        taken_book = stub.TakeBook(
            book_service_pb2.BookRequest(id=request.book_id))
        if not taken_book.success:
            return JSONResponse(
                content={"message": "There is no any book"}, status_code=404
            )

        success, borrowed_id = database.give_book(request)
        if not success:
            response = stub.ReturnBook(
                book_service_pb2.BookRequest(id=request.book_id)
            )
            return JSONResponse(
                content={"message": "Too many book has already taken"},
                status_code=409
            )

        response = {
            "message": f"reader {request.reader_id} "
            + f"take the {request.book_id} book",
            "borrowed_id": borrowed_id,
        }
        return JSONResponse(content=response, status_code=200)
    except Exception as e:
        return JSONResponse(content={"message": str(e)}, status_code=500)


@app.post("/return_book")
def return_book(
        request: model.BorrowRequest,
        token_body: dict = Depends(decode_token)):

    """
    Return book with book_id with borrowed_id
    """

    try:

        librarian = database.find_librarian_id(token_body["librarian_id"])
        if not librarian:
            return JSONResponse(
                content={"message": "Invalid token"}, status_code=401)

        borrowed_info = database.return_book(
            request.borrow_id, request.book_id)

        if not borrowed_info:
            return JSONResponse(
                content={"message": "There is no any borrowed records"},
                status_code=404
            )

        if borrowed_info == "Book has already returned":
            return JSONResponse(
                content={"message": borrowed_info}, status_code=409)

        if borrowed_info == "Wrong book was returned":
            return JSONResponse(
                content={"message": borrowed_info}, status_code=409)

        returned_book = stub.ReturnBook(
            book_service_pb2.BookRequest(id=request.book_id)
        )

        if returned_book:

            response = {
                "message": f"reader {borrowed_info['reader_id']} "
                f"return the {request.book_id} book"
            }

        else:
            response = {
                "message": f"librarian can't return the "
                f"{request.book_id} book"
            }

        return JSONResponse(content=response, status_code=200)
    except Exception as e:
        return JSONResponse(content={"message": str(e)}, status_code=500)


@app.post("/get_books")
def get_books(page_info: model.PageInfo):

    """
    Get all book with pagination where user choose page
    and number of page
    """

    try:

        returned = stub.GetBooks(
            book_service_pb2.PageInfo(
                per_page=page_info.per_page, page=page_info.page)
        )

        books = []

        for b in returned.books:
            books.append(
                {
                    "id": b.id,
                    "title": b.title,
                    "author": b.author,
                    "publish_year": b.publish_year,
                    "isbn": b.isbn,
                    "count": b.count,
                }
            )

        response = {"message": "books are returned", "books": books}

        return JSONResponse(content=response, status_code=200)
    except Exception as e:
        return JSONResponse(content={"message": str(e)}, status_code=500)


@app.get("/get_books/{reader_id}")
def get_books_per_reader(
        reader_id: str, page_info: model.PageInfo,
        token_body: dict = Depends(decode_token)):

    """
    Get all taken book for reader with pagination where user choose page
    and number of page
    """

    try:

        librarian = database.find_librarian_id(token_body["librarian_id"])
        if not librarian:
            return JSONResponse(
                content={"message": "Invalid token"}, status_code=401)

        books_ids = list(database.get_books(reader_id))

        start = page_info.per_page * (page_info.page - 1)
        end = min(((page_info.per_page * page_info.page)), len(books_ids))

        returned = stub.GetBooksForList(
            book_service_pb2.BookIdsList(
                book_ids=[
                    book_service_pb2.BookRequest(id=b_id)
                    for b_id in books_ids[start:end]
                ]
            )
        )

        books = []

        for b in returned.books:
            books.append(
                {
                    "id": b.id,
                    "title": b.title,
                    "author": b.author,
                    "publish_year": b.publish_year,
                    "isbn": b.isbn,
                    "count": b.count,
                }
            )

        response = {"message": "books are returned", "books": books}

        return JSONResponse(content=response, status_code=200)
    except Exception as e:
        return JSONResponse(content={"message": str(e)}, status_code=500)
