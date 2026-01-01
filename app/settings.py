from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Lee DATABASE_URL desde env vars automáticamente; default SQLite local
    database_url: str = "sqlite:///./local.db"

    # test_database_url para tests explícitos con Postgres
    test_database_url: str = (
        "postgresql+psycopg://app_user:app_password@localhost:5433/app_test_db"
    )


settings = Settings()
