import pytest
import pytest_asyncio
import os

from redis.asyncio import Redis
from app.settings import settings
from httpx import AsyncClient, ASGITransport
from app.main import create_app
from app.db import Base, create_engine, sessionmaker
from sqlalchemy import text


# Use DATABASE_URL when provided (CI uses Postgres); fallback to local SQLite for dev
db_url = settings.database_url
is_sqlite = db_url.startswith("sqlite")

if is_sqlite:
    TEST_DB_FILE = "test_db.sqlite"
    engine_test = create_engine(f"sqlite:///{TEST_DB_FILE}", echo=False)
else:
    TEST_DB_FILE = None
    engine_test = create_engine(db_url, echo=False)

SessionTest = sessionmaker(autocommit=False, autoflush=False, bind=engine_test)


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    # For SQLite fallback, create/drop tables; for Postgres assume migrations already ran
    if is_sqlite:
        Base.metadata.create_all(bind=engine_test)
    yield
    if is_sqlite:
        Base.metadata.drop_all(bind=engine_test)
        engine_test.dispose()
        if TEST_DB_FILE and os.path.exists(TEST_DB_FILE):
            try:
                os.remove(TEST_DB_FILE)
            except Exception:
                pass  # File might still be in use


@pytest_asyncio.fixture
async def async_client():
    import app.db as db_module
    from app.users.routes import get_db

    # Patch the app.db module to use our test database
    original_engine = db_module.engine
    original_sessionlocal = db_module.SessionLocal

    db_module.engine = engine_test
    db_module.SessionLocal = SessionTest

    # Create app with test database
    app = create_app()

    # Override the get_db dependency to use test database
    def override_get_db():
        session = SessionTest()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db

    # Clear data before each test
    session = SessionTest()
    try:
        session.execute(text("DELETE FROM users;"))
        session.commit()
    except Exception:
        pass
    finally:
        session.close()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    # Clear data after each test
    session = SessionTest()
    try:
        session.execute(text("DELETE FROM users;"))
        session.commit()
    except Exception:
        pass
    finally:
        session.close()

    # Restore original after test
    db_module.engine = original_engine
    db_module.SessionLocal = original_sessionlocal


@pytest_asyncio.fixture
async def redis_client(request):
    try:
        redis = Redis.from_url(settings.redis_url, decode_responses=True)
        await redis.ping()  # Test connection
        await redis.flushdb()  # Clear all data before test
        yield redis
        await redis.flushdb()  # Clear all data after test
        await redis.aclose()
    except Exception as e:
        # Skip tests that require Redis if it's not available
        pytest.skip(f"Redis not available: {e}")
