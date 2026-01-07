from sqlalchemy import create_engine, text
from app.auth.security import hash_password

db_url = "postgresql+psycopg://app_user:app_password@localhost:5433/app_test_db"
engine = create_engine(db_url)

with engine.begin() as conn:
    # Eliminar usuario existente
    conn.execute(text("DELETE FROM users WHERE email = 'user@example.com'"))

    # Crear nuevo hash con argon2
    password_hash = hash_password("1234")

    # Insertar usuario con nuevo hash
    conn.execute(
        text(
            "INSERT INTO users (email, full_name, password_hash) VALUES (:email, :full_name, :hash)"
        ),
        {"email": "user@example.com", "full_name": "Test User", "hash": password_hash},
    )

print("✓ Usuario recreado con hash argon2")
print(f"✓ Hash: {password_hash[:50]}...")
