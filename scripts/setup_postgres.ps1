# Setup PostgreSQL for backend-foundations
# Este script levanta PostgreSQL y crea las tablas necesarias

Write-Host "Setting up PostgreSQL..." -ForegroundColor Cyan

# 1. Levantar PostgreSQL con Docker
Write-Host "`n1. Levantando PostgreSQL container..." -ForegroundColor Yellow
docker compose up db -d

if ($LASTEXITCODE -ne 0) {
    Write-Host "Error al levantar PostgreSQL. Esta Docker corriendo?" -ForegroundColor Red
    exit 1
}

Start-Sleep -Seconds 3

# 2. Crear las tablas
Write-Host "`n2. Creando tablas en la base de datos..." -ForegroundColor Yellow
$env:DATABASE_URL = "postgresql+psycopg://app_user:app_password@localhost:5433/app_db"
poetry run python -c "from app.db import engine, Base; from app.users.models import User; Base.metadata.create_all(bind=engine); print('Tablas creadas exitosamente')"

if ($LASTEXITCODE -ne 0) {
    Write-Host "Error al crear tablas. PostgreSQL esta listo?" -ForegroundColor Red
    exit 1
}

Write-Host "`nPostgreSQL configurado correctamente!" -ForegroundColor Green
Write-Host "`nPara iniciar la app con PostgreSQL:" -ForegroundColor Cyan
Write-Host '  $env:DATABASE_URL="postgresql+psycopg://app_user:app_password@localhost:5433/app_db"' -ForegroundColor White
Write-Host "  poetry run uvicorn app.main:app --reload" -ForegroundColor White
Write-Host "`nCredenciales:" -ForegroundColor Cyan
Write-Host "  Host: localhost:5433" -ForegroundColor White
Write-Host "  Usuario: app_user" -ForegroundColor White
Write-Host "  Password: app_password" -ForegroundColor White
Write-Host "  Base de datos: app_db" -ForegroundColor White
