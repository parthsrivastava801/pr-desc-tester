# Task Manager

A full-stack task management application built with Django REST Framework and React.

## Project Structure

```
├── backend/          # Django REST API
│   ├── config/       # Django project settings & URL config
│   ├── tasks/        # Core task & tag management
│   ├── manage.py
│   └── requirements.txt
├── frontend/         # React SPA (coming soon)
│   └── src/
└── README.md
```

## Features

- **Task CRUD** — Create, read, update, and delete tasks with full REST API
- **Priority Levels** — Assign Low / Medium / High / Urgent priority to tasks
- **Due Dates** — Set deadlines with automatic overdue detection
- **Status Tracking** — Move tasks through To Do → In Progress → Done
- **Color-coded Tags** — Organize tasks with custom labeled tags
- **Owner Permissions** — Only task owners can edit or delete their tasks
- **Filtering & Search** — Filter by status/priority, search by title/description
- **Pagination** — Paginated list responses (20 items per page)

## Getting Started

### Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### Frontend

```bash
cd frontend
npm install
npm start
```

The React app runs on `http://localhost:3000` and proxies API calls to `http://localhost:8000`.

## API Endpoints

### Tasks

| Method | Endpoint                 | Description                        | Auth Required |
|--------|--------------------------|------------------------------------|---------------|
| GET    | `/api/tasks/`            | List all tasks (paginated)         | Yes           |
| POST   | `/api/tasks/`            | Create a new task                  | Yes           |
| GET    | `/api/tasks/<id>/`       | Get task detail                    | Yes           |
| PUT    | `/api/tasks/<id>/`       | Full update (owner only)           | Yes           |
| PATCH  | `/api/tasks/<id>/`       | Partial update (owner only)        | Yes           |
| DELETE | `/api/tasks/<id>/`       | Delete task (owner only)           | Yes           |
| GET    | `/api/tasks/overdue/`    | List all overdue tasks             | Yes           |
| GET    | `/api/tasks/my_tasks/`   | List current user's tasks          | Yes           |

### Tags

| Method | Endpoint                 | Description                        | Auth Required |
|--------|--------------------------|------------------------------------|---------------|
| GET    | `/api/tags/`             | List all tags                      | Yes           |
| POST   | `/api/tags/`             | Create a tag                       | Yes           |
| GET    | `/api/tags/<id>/`        | Get tag detail                     | Yes           |
| PUT    | `/api/tags/<id>/`        | Update a tag                       | Yes           |
| DELETE | `/api/tags/<id>/`        | Delete a tag                       | Yes           |

## Tech Stack

- **Backend:** Python 3.12+, Django 4.2, Django REST Framework
- **Frontend:** React 18, Axios (coming soon)
- **Database:** SQLite (dev), PostgreSQL (prod)
