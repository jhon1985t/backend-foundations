from sqlalchemy import inspect, select
from app.db import Base, engine, SessionLocal
from app.users.models import User
from app.auth.security import hash_password


def init_schema_and_seed() -> None:
    # Create all tables
    Base.metadata.create_all(bind=engine)

    # Verify tables
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f"✓ Tables present: {tables}")
    if "users" not in tables:
        raise RuntimeError("users table was not created")

    # Seed test user if missing
    db = SessionLocal()
    try:
        existing = db.scalar(select(User).where(User.email == "user@example.com"))
        if not existing:
            user = User(
                email="user@example.com",
                full_name="Test User",
                password_hash=hash_password("1234"),
            )
            db.add(user)
            db.commit()
            print("✓ Seeded test user: user@example.com")
        else:
            print("✓ Test user already exists; skipping seed")
    finally:
        db.close()


if __name__ == "__main__":
    init_schema_and_seed()
