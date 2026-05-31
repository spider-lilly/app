# Mitrova API

Django REST Framework implementation of the original FastAPI auth API.

## Setup

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## Environment

```env
DEBUG=True
SECRET_KEY=change-me
DATABASE_URL=sqlite:///db.sqlite3
ALLOWED_HOSTS=localhost,127.0.0.1
EXPIRE_MINS=30
ALGORITHM=HS256
```

## Endpoints

- `GET /` health check
- `POST /api/register/`
- `POST /api/login/`
- `POST /api/Login/` compatibility alias for the old route casing
- `GET /api/profile/`

Authenticated requests use:

```http
Authorization: Bearer <access_token>
```
