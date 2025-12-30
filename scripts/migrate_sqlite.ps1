# Run Alembic migrations using SQLite (local.db)
Write-Host "Running Alembic migrations with SQLite..." -ForegroundColor Cyan

# Clear DATABASE_URL to force SQLite default
if (Test-Path Env:DATABASE_URL) {
    Remove-Item Env:DATABASE_URL
}

poetry run alembic upgrade head

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Migration failed" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Migrations applied to SQLite (./local.db)" -ForegroundColor Green
