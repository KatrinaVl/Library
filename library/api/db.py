import uuid

from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


DATABASE_URL = "postgresql://KV:KV_pass@database:5432/library_db"

Base = declarative_base()

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

""" tables description """

class Users(Base):
    __tablename__ = 'users'
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)

class Librarians(Base):
    __tablename__ = 'librarians'
    id = Column(String, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)

""" actions with tables """

def create_librarian(lib: dict):

    add_info = Librarians(id=str(uuid.uuid4()), email=lib['email'], password=lib['password'])

    db = SessionLocal()

    db.add(add_info)
    db.commit()
    db.refresh(add_info)
    db.close()

    return add_info


def find_librarian(lib: dict):

    db = SessionLocal()
    librarian = db.query(Librarians).filter(Librarians.email == lib['email']).first()
    db.close()

    return librarian



