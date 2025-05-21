from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import uuid

DATABASE_URL = "postgresql://KV:KV_pass@database:5432/library_db"

Base = declarative_base()

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

""" tables description """


class Books(Base):
    __tablename__ = "books"
    id = Column(String, primary_key=True)
    title = Column(String, unique=True, nullable=False)
    author = Column(String, nullable=False)
    publish_year = Column(Integer, nullable=False)
    isbn = Column(String)
    count = Column(Integer, default=1)


""" actions with tables """


def create_book(book_info):
    book_id = str(uuid.uuid4())
    db = SessionLocal()

    book = Books(
        id=book_id,
        title=book_info["title"],
        author=book_info["author"],
        publish_year=book_info["publish_year"],
        isbn=book_info["isbn"],
        count=book_info["count"],
    )

    db.add(book)
    db.commit()
    db.refresh(book)
    db.close()

    return book


def update_book(book_info):
    db = SessionLocal()
    book = db.query(Books).filter(Books.id == book_info["id"]).first()

    if not book:
        return None

    book.title = book_info["title"]
    book.author = book_info["author"]
    book.publish_year = book_info["publish_year"]
    book.isbn = book_info["isbn"]
    book.count = book_info["count"]

    db.commit()
    db.refresh(book)
    db.close()
    return book


def get_book(book_id):
    db = SessionLocal()
    book = db.query(Books).filter(Books.id == book_id).first()

    if not book:
        return None

    db.close()
    return book


def delete_book(book_id):
    db = SessionLocal()
    book = db.query(Books).filter(Books.id == book_id).first()

    if book:
        db.delete(book)
        db.commit()

    db.close()


def take_book(book_id):

    db = SessionLocal()
    book = db.query(Books).filter(Books.id == book_id).first()

    if not book:
        return None

    if book.count > 0:
        book.count -= 1
        db.commit()
        db.refresh(book)
        db.close()
        return True

    db.close()

    return False


def return_book(book_id):
    db = SessionLocal()
    book = db.query(Books).filter(Books.id == book_id).first()

    if not book:
        db.close()
        return False

    book.count += 1

    db.commit()
    db.refresh(book)
    db.close()

    return True


def get_books():

    db = SessionLocal()
    books = db.query(Books).all()

    db.close()
    return books


def get_books_for_list(book_ids):

    db = SessionLocal()
    books = []
    for b_id in book_ids:
        book = db.query(Books).filter(Books.id == b_id).first()
        books.append(book)

    db.close()
    return books
