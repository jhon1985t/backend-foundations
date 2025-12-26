import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# Use env var if provided; default to local SQLite to keep tests/CI working
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite+pysqlite:///./local.db",
)


class Base(DeclarativeBase):
    pass


engine = create_engine(DATABASE_URL, echo=False)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
