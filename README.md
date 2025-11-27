# account-service

This service manages user accounts for the UMASS project. It is a Django project.

* More Detail just Open **docs/build/html/index.html** in your browser.

Account Service is a lightweight Django REST API that manages user account records for the wider platform. It exposes CRUD endpoints under `/api/account/` and is designed to sit behind an authentication service that issues JWTs. Incoming requests are authenticated locally (no network hop) using the shared signing key, and role-based permissions (`ADMIN`, `STAFF`, `STUDENT`) gate each operation.

Key capabilities:

- Create, read, update, and delete accounts keyed by email
- Count, list, and filter accounts by role, creation date, or activity status
- Activate/deactivate accounts and enforce owner-or-admin write access
- Health and welcome endpoints for quick service checks

Out of the box it runs on port `9001` (via `manage.py runserver 9001`) with SQLite storage, but the stack is portable to other databases supported by Django.

## Overview

- Framework: Django + Django REST Framework
- Auth: JWT via `rest_framework_simplejwt`, decoded locally with a shared signing key
- Data: SQLite by default (`db.sqlite3`), easy to swap via Django `DATABASES` settings
- Domain: Account records with email uniqueness, role, active flag, timestamps, and creator id from the token

## Documentation

- Sphinx docs live under `docs/`. Build with `cd docs && make html` and open `docs/build/html/index.html`.
- Key pages: overview, API endpoints, and testing instructions.

## How to Compile and Run

1) Install dependencies: `pip install -r requirements.txt`
2) (Optional) Apply migrations if changing databases: `python manage.py migrate`
3) Seed sample data (if desired): `python manage.py loaddata fixtures/initial_data.json`
4) Start the server: `python manage.py runserver 9001`
5) Hit the API (default base path `/api/`), e.g. `GET http://localhost:9001/api/account/`

## Python Version and Environment

- Developed with Python 3.13 (works with any Django-supported Python 3.x).
- Recommended: use a virtual environment: `python -m venv .venv && source .venv/bin/activate` (Unix/macOS) or `.venv\\Scripts\\activate` (Windows).

## All Features

- CRUD: create, fetch single by email, list, update, delete.
- Filtering: list by role, active/inactive, created after a given timestamp, updated before a timestamp.
- Metrics: count all accounts, count by role.
- Lifecycle: activate/deactivate accounts.
- Ownership and RBAC: `ADMIN` full access; `STUDENT`/`STAFF` limited; owner-or-admin check on mutations.
- Utilities: health check (`/api/health/`), welcome banner (`/api/welcome/`), API overview map (`/api/`).

## Testing

- Django test runner (includes tests in `accountService/base/tests.py`): `cd accountService && python manage.py test`
- Pytest suite (includes app-level `tests/test_account_api.py`): `cd accountService && pytest` or target a file: `pytest tests/test_account_api.py`
- To keep environments clean, activate your venv first: `source .venv/bin/activate`
- All test cases result show on alltests_report.html

## Project Structure

- `accountService/` root Django project
- `accountService/accountService/` core settings, URLs, WSGI/ASGI, JWT auth helper
- `accountService/api/` views, serializers, permissions, URL routing
- `accountService/base/` Django models and admin setup
- `accountService/fixtures/` optional seed data
- `manage.py` Django entrypoint

## Authentication

- Requests expect a `bearer <token>` Authorization header containing a JWT signed with the configured key (`SIMPLE_JWT["SIGNING_KEY"]`).
- The token should include `user_id`, `email`, `username`, and `role` claims. Role controls access (`ADMIN`, `STAFF`, `STUDENT`).

## API Endpoints (base path `/api/`)

- `GET /account/` — list all accounts (admin)
- `GET /account/get/<email>/` — fetch one (student/admin/staff)
- `POST /account/create/` — create; email/role/creator taken from token (student/admin/staff)
- `PUT /account/update/` — update; owner or admin
- `DELETE /account/delete/` — delete; owner or admin
- `GET /account/count/` — total count (admin)
- `GET /account/count_by_role/<role>/` — count by role (admin)
- `GET /account/created_after/<iso-datetime>/` — filter by created date (admin)
- `GET /account/updated_before/<iso-datetime>/` — filter by updated date (admin)
- `GET /account/role/<role>/` — filter by role (admin)
- `PUT /account/activate/` — set `is_active=True` (admin)
- `PUT /account/deactivate/` — set `is_active=False` (admin)
- `GET /account/active/` — list active accounts (admin)
- `GET /account/inactive/` — list inactive accounts (admin)
- `GET /health/` — health probe
- `GET /welcome/` — welcome message
- `GET /` — overview map of endpoints
