from datetime import datetime
from pydantic import BaseModel, EmailStr, Field

""" data validation """

class User(BaseModel):
    name: str
    email: EmailStr

class Librarian(BaseModel):
    email: EmailStr
    password: str




