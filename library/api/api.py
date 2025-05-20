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


""" actions with token """

SECRET_KEY = "Library__"
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def create_token(data, expires_time=timedelta(minutes=30)):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_time
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str = Depends(oauth2_scheme)):
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return decoded
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


@app.post("/register")
def register(request: model.Librarian):
    try:
        hash_password = hashlib.sha256(request.password.encode())
        hex_dig = hash_password.hexdigest()

        database.create_librarian({"email": request.email,
                                   "password": hex_dig})

        return JSONResponse(
            content={"message": "registration is successful"}, status_code=200
        )
    except Exception as e:
        return JSONResponse(content={"message": str(e)}, status_code=400)


@app.post("/login")
def login(request: model.Librarian):

    try:
        librarian = database.find_librarian(
            {"email": request.email, "password": request.password}
        )

        hash_password = hashlib.sha256(request.password.encode())
        hex_dig = hash_password.hexdigest()

        if hex_dig != librarian.password:
            return JSONResponse(content={"message": "wrong password"},
                                status_code=400)

        token = create_token({"librarian_id": librarian.id})

        return JSONResponse(content={"token": token}, status_code=200)

    except Exception as e:
        return JSONResponse(content={"message": str(e)}, status_code=400)


@app.post("/register_book")
def register_book(request: model.BookInfo,
                  token_body: dict = Depends(decode_token)):
    try:

        librarian = database.find_librarian_id(token_body["librarian_id"])
        if not librarian:
            raise HTTPException(status_code=401, detail="Invalid token")

        response_book = stub.CreateBook(
            book_service_pb2.CreateBookRequest(**request.dict())
        )

        response = {
            "message": "register information is successful",
            "book": MessageToDict(response_book),
        }

        return JSONResponse(content=response, status_code=200)
    except Exception as e:
        return JSONResponse(content={"message": str(e)}, status_code=400)


@app.post("/update_book")
def update_book(request: model.BookInfo,
                token_body: dict = Depends(decode_token)):
    try:

        librarian = database.find_librarian_id(token_body["librarian_id"])
        if not librarian:
            raise HTTPException(status_code=401, detail="Invalid token")

        response_book = stub.UpdateBook(
            book_service_pb2.UpdateBookRequest(**request.dict())
        )

        response = {
            "message": "changing information is successful",
            "book": MessageToDict(response_book),
        }
        return JSONResponse(content=response, status_code=200)
    except Exception as e:
        return JSONResponse(content={"message": str(e)}, status_code=400)


@app.get("/get_book/{book_id}")
def get_book(book_id: str, token_body: dict = Depends(decode_token)):
    try:

        librarian = database.find_librarian_id(token_body["librarian_id"])
        if not librarian:
            raise HTTPException(status_code=401, detail="Invalid token")

        response_book = stub.GetBook(book_service_pb2.BookRequest(id=book_id))

        response = {"message": "book is found",
                    "book": MessageToDict(response_book)}
        return JSONResponse(content=response, status_code=200)
    except Exception as e:
        return JSONResponse(content={"message": str(e)}, status_code=400)


@app.delete("/delete_book/{book_id}")
def delete_book(book_id: str, token_body: dict = Depends(decode_token)):
    try:

        librarian = database.find_librarian_id(token_body["librarian_id"])
        if not librarian:
            raise HTTPException(status_code=401, detail="Invalid token")

        response = {"message": "book is deleted"}
        return JSONResponse(content=response, status_code=200)
    except Exception as e:
        return JSONResponse(content={"message": str(e)}, status_code=400)


@app.post("/add_reader")
def add_reader(reader: model.Reader, token_body: dict = Depends(decode_token)):
    try:

        librarian = database.find_librarian_id(token_body["librarian_id"])
        if not librarian:
            raise HTTPException(status_code=401, detail="Invalid token")

        database.add_reader(reader)
        response = {"message": "reader is added"}
        return JSONResponse(content=response, status_code=200)

    except Exception as e:
        return JSONResponse(content={"message": str(e)}, status_code=400)


@app.post("/update_reader/{reader_id}")
def update_reader(reader_id: str, reader: model.Reader,
                  token_body: dict = Depends(decode_token)):
    try:

        librarian = database.find_librarian_id(token_body["librarian_id"])
        if not librarian:
            raise HTTPException(status_code=401, detail="Invalid token")

        new_reader = database.update_reader(reader, reader_id)
        response = {
            "message": "information about reader has changed",
            "reader": {"name": new_reader.name, "email": new_reader.email},
        }
        return JSONResponse(content=response, status_code=200)

    except Exception as e:
        return JSONResponse(content={"message": str(e)}, status_code=400)


@app.get("/get_reader/{reader_id}")
def get_reader(reader_id: str, token_body: dict = Depends(decode_token)):
    try:

        librarian = database.find_librarian_id(token_body["librarian_id"])
        if not librarian:
            raise HTTPException(status_code=401, detail="Invalid token")

        reader = database.get_reader(reader_id)

        response = {
            "message": "reader is found",
            "reader": {"name": reader.name, "email": reader.email},
        }
        return JSONResponse(content=response, status_code=200)
    except Exception as e:
        return JSONResponse(content={"message": str(e)}, status_code=400)


@app.delete("/delete_reader/{reader_id}")
def delete_reader(reader_id: str, token_body: dict = Depends(decode_token)):
    try:

        librarian = database.find_librarian_id(token_body["librarian_id"])
        if not librarian:
            raise HTTPException(status_code=401, detail="Invalid token")

        reader = database.delete_reader(reader_id)

        if not reader:
            raise HTTPException(status_code=401, detail="Reader is not found")

        response = {
            "message": "reader is deleted",
            "reader": {"name": reader.name, "email": reader.email},
        }
        return JSONResponse(content=response, status_code=200)
    except Exception as e:
        return JSONResponse(content={"message": str(e)}, status_code=400)
