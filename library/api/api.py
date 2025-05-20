from datetime import datetime, timedelta

import jwt
import hashlib
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from api.db import Base, engine
from . import db, model

app = FastAPI()

# Base.metadata.create_all(bind=engine)

""" actions with token """

SECRET_KEY = "Library__"
ALGORITHM = "HS256"

def create_token(data, expires_time = timedelta(minutes=30)):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_time
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token):
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return decoded
    except jwt.ExpiredSignatureError:
        return "Token expired"
    except jwt.InvalidTokenError:
        return "Invalid token"

@app.post("/register")
def register(request: model.Librarian):
    try:
        hash_password = hashlib.sha256(request.password.encode())
        hex_dig = hash_password.hexdigest()

        librarian = db.create_librarian({"email" : request.email, "password" : hex_dig})
    
        return {"message" : "registration is successful"}, 200
    except Exception as e:
        return {"message" : str(e)}

@app.post("/login")
def login(request: model.Librarian):
    
    try:
        librarian = db.find_librarian({"email" : request.email, "password" : request.password})

        hash_password = hashlib.sha256(request.password.encode())
        hex_dig = hash_password.hexdigest()

        if (hex_dig != librarian.password):
            return {"message" : "wrong password"}, 400

        token = create_token({"email" : request.email})
    
        return {"token" : token}, 200

    except Exception as e:
        return {"message" : str(e)}
