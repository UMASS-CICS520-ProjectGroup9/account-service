Overview
========

Account Service is a lightweight Django REST API that manages user account records for the wider platform. It exposes CRUD endpoints under ``/api/account/`` and is designed to sit behind an authentication service that issues JWTs. Incoming requests are authenticated locally using the shared signing key, and role-based permissions (``ADMIN``, ``STAFF``, ``STUDENT``) gate each operation.

Key capabilities
----------------

- Create, read, update, and delete accounts keyed by email
- Count, list, and filter accounts by role, creation date, or activity status
- Activate/deactivate accounts and enforce owner-or-admin write access
- Health and welcome endpoints for quick service checks

Stack and runtime
-----------------

- Framework: Django + Django REST Framework
- Auth: JWT via ``rest_framework_simplejwt``, decoded locally with a shared signing key
- Data: SQLite by default (``db.sqlite3``), configurable via Django ``DATABASES``
- Default port: ``9001`` (``python manage.py runserver 9001``)

Quickstart
----------

1. Install dependencies: ``pip install -r requirements.txt``
2. (Optional) Migrate if changing databases: ``python manage.py migrate``
3. (Optional) Seed data: ``python manage.py loaddata fixtures/initial_data.json``
4. Run the server: ``python manage.py runserver 9001``
5. Call the API at ``http://localhost:9001/api/``

Environment
-----------

- Developed with Python 3.13 (works with any Django-supported Python 3.x)
- Recommended: virtualenv ``python -m venv .venv && source .venv/bin/activate`` (macOS/Linux) or ``.venv\\Scripts\\activate`` (Windows)

Project structure
-----------------

- ``accountService/`` root Django project
- ``accountService/accountService/`` core settings, URLs, WSGI/ASGI, JWT auth helper
- ``accountService/api/`` views, serializers, permissions, URL routing
- ``accountService/base/`` models and admin setup
- ``accountService/fixtures/`` optional seed data
- ``manage.py`` Django entrypoint

Authentication
--------------

- Authorization header: ``bearer <token>``
- JWT claims expected: ``user_id``, ``email``, ``username``, ``role``
- Roles: ``ADMIN`` (full access), ``STAFF``/``STUDENT`` (limited), owner-or-admin on mutations
