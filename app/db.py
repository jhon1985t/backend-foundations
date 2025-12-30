import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# SQLite by default (works in local and CI)
# Override with DATABASE_URL env var only if you need Postgres
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./local.db")


class Base(DeclarativeBase):
    pass


engine = create_engine(DATABASE_URL, echo=False)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
