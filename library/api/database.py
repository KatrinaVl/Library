import uuid

from sqlalchemy import Column, String, Integer, create_engine, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from . import model
from datetime import datetime


DATABASE_URL = "postgresql://KV:KV_pass@database:5432/library_db"

Base = declarative_base()

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

""" tables description """


class Readers(Base):
    __tablename__ = "readers"
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    count = Column(Integer, default=0)


class Librarians(Base):
    __tablename__ = "librarians"
    id = Column(String, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)


class BorrowedBooks(Base):
    __tablename__ = "borrowed_books"
    id = Column(String, primary_key=True)
    book_id = Column(String, nullable=False)
    reader_id = Column(String, nullable=False)
    borrow_date = Column(DateTime, nullable=False)
    return_date = Column(DateTime, nullable=True)


""" actions with tables """


def create_librarian(lib: dict):

    add_info = Librarians(
        id=str(uuid.uuid4()), email=lib["email"], password=lib["password"]
    )

    db = SessionLocal()

    db.add(add_info)
    db.commit()
    db.refresh(add_info)
    db.close()

    return add_info


def find_librarian(lib: dict):

    db = SessionLocal()
    librarian = db.query(Librarians).filter(
        Librarians.email == lib["email"]).first()
    db.close()

    return librarian


def find_librarian_id(lib_id):

    db = SessionLocal()
    librarian = db.query(Librarians).filter(Librarians.id == lib_id).first()
    db.close()

    return librarian


def add_reader(reader: model.Reader):

    add_reader = Readers(
        id=str(uuid.uuid4()),
        email=reader.email,
        name=reader.name)

    db = SessionLocal()

    db.add(add_reader)
    db.commit()
    db.refresh(add_reader)
    db.close()

    return add_reader


def update_reader(reader: model.Reader, reader_id):
    db = SessionLocal()

    old_reader = db.query(Readers).filter(Readers.id == reader_id).first()
    if not reader:
        return None

    old_reader.name = reader.name
    old_reader.email = reader.email

    db.commit()
    db.refresh(old_reader)
    db.close()

    return old_reader


def get_reader(reader_id):
    db = SessionLocal()

    old_reader = db.query(Readers).filter(Readers.id == reader_id).first()

    db.close()

    return old_reader


def delete_reader(reader_id):
    db = SessionLocal()

    old_reader = db.query(Readers).filter(Readers.id == reader_id).first()
    if not old_reader:
        return None

    info_reader = model.Reader(name=old_reader.name, email=old_reader.email)
    db.delete(old_reader)
    db.commit()
    db.close()

    return info_reader


def give_book(request: model.GiveRequest):
    db = SessionLocal()

    reader = db.query(Readers).filter(Readers.id == request.reader_id).first()

    if reader.count == 3:
        return (False, None)

    reader.count += 1

    db.commit()
    db.refresh(reader)

    borrowed_id = str(uuid.uuid4())

    add_taken_book = BorrowedBooks(
        id=borrowed_id,
        book_id=request.book_id,
        reader_id=request.reader_id,
        borrow_date=datetime.utcnow(),
    )

    db.add(add_taken_book)
    db.commit()
    db.refresh(add_taken_book)
    db.close()

    return (True, borrowed_id)


def return_book(borrowed_id: str, returned_book_id: str):
    db = SessionLocal()

    info = db.query(BorrowedBooks).filter(
        BorrowedBooks.id == borrowed_id).first()

    if not info:
        return None

    if info.return_date:
        return "Book has already returned"

    if info.book_id != returned_book_id:
        return "Wrong book was returned"

    info.return_date = datetime.utcnow()

    response = {"book_id": info.book_id, "reader_id": info.reader_id}

    db.commit()
    db.refresh(info)

    reader = db.query(Readers).filter(Readers.id == info.reader_id).first()

    reader.count -= 1

    db.commit()
    db.refresh(reader)

    db.close()

    return response


def get_books(reader_id):

    db = SessionLocal()

    books = db.query(BorrowedBooks).filter(
        BorrowedBooks.reader_id == reader_id,
        BorrowedBooks.return_date.is_(None)
    )

    books_ids = [b.book_id for b in books]

    db.close()

    return books_ids
