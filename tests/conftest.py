import pytest
import pytest_asyncio

from httpx import AsyncClient, ASGITransport
from app.main import create_app
from app.db import Base, create_engine, sessionmaker
from sqlalchemy import text


# Use SQLite for tests (in-memory for isolation)
engine_test = create_engine("sqlite:///:memory:", echo=False)
SessionTest = sessionmaker(autocommit=False, autoflush=False, bind=engine_test)


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    # Create the database tables once for all tests
    Base.metadata.create_all(bind=engine_test)
    yield
    # Drop the database tables after all tests
    Base.metadata.drop_all(bind=engine_test)


@pytest_asyncio.fixture
async def async_client():
    import app.db as db_module

    # Patch the app.db module to use our test in-memory database
    original_engine = db_module.engine
    original_sessionlocal = db_module.SessionLocal

    db_module.engine = engine_test
    db_module.SessionLocal = SessionTest

    # Create app with test database
    app = create_app()

    # Clear data before each test
    session = SessionTest()
    try:
        session.execute(text("DELETE FROM users;"))
        session.commit()
    except Exception:
        pass  # Table might not exist yet
    finally:
        session.close()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    # Restore original after test
    db_module.engine = original_engine
    db_module.SessionLocal = original_sessionlocal
