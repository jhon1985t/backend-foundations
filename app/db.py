from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.settings import settings


class Base(DeclarativeBase):
    pass


# DATABASE_URL viene de settings (lee env vars con prioridad automática)
engine = create_engine(settings.database_url, echo=False)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
