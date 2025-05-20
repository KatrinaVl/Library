import uuid

from sqlalchemy import Column, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from . import model


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


class Librarians(Base):
    __tablename__ = "librarians"
    id = Column(String, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)


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

    add_reader = Readers(id=str(uuid.uuid4()),
                         email=reader.email, name=reader.name)

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

    return info_reader
