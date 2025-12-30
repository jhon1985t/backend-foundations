# Alembic Migrations Guide

Alembic is used for database schema versioning and migrations.

## Quick Start

### SQLite (Default)

```bash
# Create a new migration (auto-detect schema changes)
poetry run alembic revision --autogenerate -m "Add users table"

# Apply pending migrations
poetry run alembic upgrade head

# Check current migration version
poetry run alembic current

# Downgrade to previous version
poetry run alembic downgrade -1
```

### PostgreSQL

If using PostgreSQL, set `DATABASE_URL` before running alembic commands:

```powershell
$env:DATABASE_URL="postgresql+psycopg://app_user:app_password@localhost:5433/app_db"

# Create migration (uses Postgres)
poetry run alembic revision --autogenerate -m "Add users table"

# Apply migrations
poetry run alembic upgrade head
```

## Configuration

- **alembic.ini**: Main configuration file
  - `sqlalchemy.url = sqlite:///./local.db` (default)
  - Override with `DATABASE_URL` environment variable for Postgres

- **alembic/env.py**: Migration environment script
  - Respects `DATABASE_URL` env var
  - Detects schema changes automatically

- **alembic/versions/**: Migration scripts directory
  - Each migration is timestamped and versioned

## Common Commands

```bash
# Initialize (already done, don't repeat)
poetry run alembic init alembic

# Generate migration from model changes
poetry run alembic revision --autogenerate -m "Description of changes"

# Apply all pending migrations
poetry run alembic upgrade head

# Apply specific migration
poetry run alembic upgrade <revision>

# Downgrade one migration
poetry run alembic downgrade -1

# View migration history
poetry run alembic history

# Show current migration version
poetry run alembic current
```

## Tips

- Always review auto-generated migrations before applying
- Use descriptive names: `alembic revision --autogenerate -m "Add email_verified column to users"`
- Keep migrations idempotent (can run multiple times safely)
- Don't modify applied migrations; create new ones for changes
