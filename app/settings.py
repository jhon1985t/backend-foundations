from pydantic_settings import BaseSettings, SettingsConfigDict
import os


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Lee DATABASE_URL desde env vars automáticamente; default SQLite local
    # Para CI/tests, usa os.getenv() para asegurar que el env var se lee siempre
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./local.db")

    # JWT settings
    jwt_secret_key: str = "CHANGE_ME"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30

    # test_database_url para tests explícitos con Postgres
    test_database_url: str = (
        "postgresql+psycopg://app_user:app_password@localhost:5433/app_test_db"
    )

    # Redis URL (override via env var REDIS_URL); default matches docker-compose (host port 6380)
    redis_url: str = "redis://localhost:6380/0"

    # Kafka (optional)
    kafka_enabled: bool = False
    kafka_bootstrap_servers: str = "localhost:9093"
    kafka_topic_user_events: str = "user-events"


settings = Settings()
