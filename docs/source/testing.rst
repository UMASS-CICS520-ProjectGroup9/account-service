Testing
=======

Django test runner
------------------

- Run from the project directory: ``cd accountService && python manage.py test``
- Executes tests under ``accountService/base/tests.py`` and other Django apps.

Pytest
------

- Run the whole suite: ``cd accountService && pytest``
- Run a specific file: ``cd accountService && pytest tests/test_account_api.py``
- Activate your virtualenv first: ``source .venv/bin/activate`` (macOS/Linux) or ``.venv\\Scripts\\activate`` (Windows)

Reports
-------

- If you generate HTML reports (e.g., with ``pytest --html=alltests_report.html --self-contained-html``), open the file locally in your browser.
