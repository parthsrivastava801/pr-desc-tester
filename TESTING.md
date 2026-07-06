# Testing Guide

A quick reference for running, writing, and extending tests in this project.

---

## Running Tests

```bash
# From the backend/ directory
cd backend

# Run all tests
python manage.py test tasks

# Run a specific test class
python manage.py test tasks.tests.TaskAPITest

# Run a specific test method
python manage.py test tasks.tests.OverdueEndpointTest.test_overdue_returns_only_overdue

# Run with verbosity
python manage.py test tasks --verbosity=2

# Run and keep the test DB for inspection
python manage.py test tasks --keepdb
```

---

## Test Structure

```
backend/tasks/tests.py
├── TaskModelTest          — Unit tests for the Task model
├── TagModelTest           — Unit tests for the Tag model
├── TaskAPITest            — CRUD + filter/search API tests
├── OverdueEndpointTest    — GET /api/tasks/overdue/ tests
├── MyTasksEndpointTest    — GET /api/tasks/my_tasks/ tests
└── TagAPITest             — Tag CRUD + assignment tests
```

---

## Fixtures

Pre-baked seed data lives in `backend/tasks/fixtures/`.

```bash
# Load sample tags into the DB
python manage.py loaddata tasks/fixtures/tags.json
```

---

## Utility Helpers (`tasks/utils.py`)

| Function | Description |
|---|---|
| `get_task_summary(user)` | Returns total/todo/in_progress/done/overdue counts |
| `get_priority_breakdown(user)` | Returns per-priority task counts |
| `get_overdue_tasks(user)` | Returns queryset of overdue tasks |
| `bulk_update_status(task_ids, status, user)` | Bulk status update with ownership guard |

---

## Writing New Tests

- Extend `django.test.TestCase` for DB isolation.
- Use `rest_framework.test.APIClient` for endpoint tests.
- Use `force_authenticate(user=...)` — do not test with raw credentials unless testing auth flows.
- Always clean up test data via `setUp` / `tearDown`; Django rolls back after each test automatically.
- Prefer `assertIn` / `assertNotIn` over index-based assertions for list results (ordering may vary).

---

## CI Notes

Tests run automatically on every push via GitHub Actions (`.github/workflows/` — to be added).
The test database is SQLite in-memory; no external services required.
