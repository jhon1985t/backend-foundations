# Changelog

All notable changes to this project will be documented in this file.

## [2026-01-07] CI hardening + Docker smoke tests
- Migrate tests to file-based SQLite `./test_db.sqlite` for reproducibility.
- Add pre-pytest DB diagnostics in CI (print `DATABASE_URL`, engine URL, tables, users count).
- Seed test user via `scripts/init_test_db.py` (email `user@example.com`, password `1234`, Argon2 hash).
- Update Dockerfile with `INSTALL_DEV` build arg to include dev dependencies (pytest/httpx).
- Install `librdkafka` and `libffi` in Docker image for `confluent-kafka` and `argon2-cffi` compatibility.
- Pass `DATABASE_URL=sqlite:///./test_db.sqlite` to container tests in CI.

## [2026-01-05] Auth hashing migration
- Switch password hashing from bcrypt to Argon2 via Passlib for Python 3.13 compatibility.
- Update dependencies: `passlib[argon2]`, `argon2-cffi`.
- Adjust tests to verify Argon2 hashes.
