import pytest
import pytest_asyncio
import os
from sqlalchemy.exc import OperationalError

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


# Try to create engine with the configured URL; if it fails, fall back to SQLite
def _get_test_engine():
    try:
        engine = create_engine(TEST_DATABASE_URL, echo=False)
        # Test the connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return engine
    except (OperationalError, Exception):
        # Fall back to SQLite (file-based for better test isolation)
        print("⚠️  Postgres not available, falling back to SQLite for tests")
        return create_engine("sqlite:///test_db.sqlite", echo=False)


engine_test = _get_test_engine()
SessionTest = sessionmaker(autocommit=False, autoflush=False, bind=engine_test)


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    # Create the database tables
    try:
        Base.metadata.create_all(bind=engine_test)
    except OperationalError as e:
        print(f"⚠️  Failed to create tables: {e}")
    yield
    # Drop the database tables after tests (if connection available)
    try:
        Base.metadata.drop_all(bind=engine_test)
    except OperationalError:
        pass


@pytest.fixture
def db_session():
    session = SessionTest()
    try:
        yield session
    finally:
        session.close()


@pytest_asyncio.fixture
async def async_client(monkeypatch, db_session):
    import app.db as db_module

    # If using SQLite, we need to ensure the app uses the test database
    if "sqlite" in engine_test.url.drivername:
        # Patch the app.db module to use our test engine
        original_engine = db_module.engine
        original_sessionlocal = db_module.SessionLocal

        db_module.engine = engine_test
        db_module.SessionLocal = SessionTest

        app = create_app()

        # Restore original after app creation (so other tests can use it)
        db_module.engine = original_engine
        db_module.SessionLocal = original_sessionlocal
    else:
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
    # Clear data before each test (support both Postgres and SQLite)
    try:
        # Detect database type
        db_name = engine_test.url.drivername
        if "sqlite" in db_name:
            # SQLite syntax
            db_session.execute(text("DELETE FROM users;"))
        else:
            # Postgres syntax
            db_session.execute(text("TRUNCATE TABLE users RESTART IDENTITY CASCADE;"))
        db_session.commit()
    except Exception as e:
        # If table doesn't exist, skip
        print(f"⚠️  Could not clear users table: {e}")
    yield
