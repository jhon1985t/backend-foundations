from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.settings import settings


class Base(DeclarativeBase):
    pass


# DATABASE_URL viene de settings (lee env vars con prioridad automática)
engine = create_engine(settings.database_url, echo=False)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Importar todos los modelos para registrarlos en Base.metadata
# DEBE ocurrir DESPUÉS de definir Base, pero ANTES de create_all
from app.users.models import User  # noqa: F401, E402
