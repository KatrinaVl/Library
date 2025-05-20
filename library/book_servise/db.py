from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql://KV:KV_pass@database:5432/library_db"

Base = declarative_base()

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

class Books(Base):
    __tablename__ = 'books'
    id = Column(String(80), primary_key=True)
    name = Column(String(120), unique=True, nullable=False)
    author = Column(String(50), nullable=False)
    publish_year = Column(Integer, nullable=False)
    isbn = Column(String(50))
    count = Column(Integer, default=1)