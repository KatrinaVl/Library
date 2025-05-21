from pydantic import BaseModel, EmailStr

""" data validation """


class Reader(BaseModel):
    name: str
    email: EmailStr


class Librarian(BaseModel):
    email: EmailStr
    password: str


class BookInfo(BaseModel):
    id: str = ""
    title: str
    author: str
    publish_year: int
    isbn: str
    count: int = 1


class BookId(BaseModel):
    id: str


class GiveRequest(BaseModel):
    book_id: str
    reader_id: str


class BorrowRequest(BaseModel):
    book_id: str
    borrow_id: str


class PageInfo(BaseModel):
    per_page: int
    page: int
