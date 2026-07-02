# Task Manager

A full-stack task management application built with Django REST Framework and React.

## Project Structure

```
├── backend/          # Django REST API
│   ├── api/          # Core task API (coming soon)
│   ├── config/       # Django project settings & URL config
│   ├── profiles/     # User profile management
│   ├── manage.py
│   └── requirements.txt
├── frontend/         # React SPA
│   ├── public/
│   └── src/
│       ├── components/   # Reusable UI components
│       ├── services/     # API client layer
│       └── index.js
└── README.md
```

## Features

- **User Profiles** — Public profile pages with avatar, bio, location, and website
- **Profile Search** — Search users by username with debounced input
- **Profile Editor** — Authenticated users can update their own profile and upload avatars
- **Auto Profile Creation** — A profile is automatically created for every new user

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

| Method | Endpoint              | Description                    | Auth Required |
|--------|-----------------------|--------------------------------|---------------|
| GET    | `/api/profiles/`      | List public profiles           | No            |
| GET    | `/api/profiles/<id>/` | Get profile detail             | No (public)   |
| GET    | `/api/profiles/me/`   | Get own profile                | Yes           |
| PATCH  | `/api/profiles/me/`   | Update own profile             | Yes           |
| PUT    | `/api/profiles/<id>/` | Full update (owner only)       | Yes           |

## Tech Stack

- **Backend:** Python 3.12+, Django 4.2, Django REST Framework
- **Frontend:** React 18, Axios
- **Database:** SQLite (dev), PostgreSQL (prod)
