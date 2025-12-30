# Run Alembic migrations using PostgreSQL

param(
    [string]$Url = "postgresql+psycopg://app_user:app_password@localhost:5433/app_db"
)

Write-Host "Running Alembic migrations with PostgreSQL..." -ForegroundColor Cyan
$env:DATABASE_URL = $Url

poetry run alembic upgrade head

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Migration failed" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Migrations applied to $env:DATABASE_URL" -ForegroundColor Green
