import pytest
import pytest_asyncio
import os

from httpx import AsyncClient, ASGITransport
from app.main import create_app
from app.db import Base, create_engine, sessionmaker
from app.users.routes import get_db
from sqlalchemy import text


# Use DATABASE_URL from environment (CI) or default for local development
TEST_DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://app_user:app_password@localhost:5433/app_test_db",
)

engine_test = create_engine(TEST_DATABASE_URL, echo=False)
SessionTest = sessionmaker(autocommit=False, autoflush=False, bind=engine_test)


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    # Create the database tables
    Base.metadata.create_all(bind=engine_test)
    yield
    # Drop the database tables after tests
    Base.metadata.drop_all(bind=engine_test)


@pytest.fixture
def db_session():
    session = SessionTest()
    try:
        yield session
    finally:
        session.close()


@pytest_asyncio.fixture
async def async_client(monkeypatch, db_session):

    app = create_app()

    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture(autouse=True)
def clear_data(db_session):
    # Clear data before each test
    db_session.execute(text("TRUNCATE TABLE users RESTART IDENTITY CASCADE;"))
    db_session.commit()
    yield
