API Endpoints
=============

Base path: ``/api/``

Accounts
--------

- ``GET /account/`` — list all accounts (admin)
- ``GET /account/get/<email>/`` — fetch one (student/admin/staff)
- ``POST /account/create/`` — create; email/role/creator taken from JWT (student/admin/staff)
- ``PUT /account/update/`` — update; owner or admin
- ``DELETE /account/delete/`` — delete; owner or admin

Filters and metrics
-------------------

- ``GET /account/count/`` — total count (admin)
- ``GET /account/count_by_role/<role>/`` — count by role (admin)
- ``GET /account/role/<role>/`` — list by role (admin)
- ``GET /account/created_after/<iso-datetime>/`` — filter by created date (admin)
- ``GET /account/updated_before/<iso-datetime>/`` — filter by updated date (admin)

Lifecycle
---------

- ``PUT /account/activate/`` — set ``is_active=True`` (admin)
- ``PUT /account/deactivate/`` — set ``is_active=False`` (admin)
- ``GET /account/active/`` — list active accounts (admin)
- ``GET /account/inactive/`` — list inactive accounts (admin)

Utilities
---------

- ``GET /health/`` — health probe
- ``GET /welcome/`` — welcome message
- ``GET /`` — overview map of endpoints
