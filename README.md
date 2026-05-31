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
DATABASE_URL=postgres://postgres:password@localhost:5432/mitrova
ALLOWED_HOSTS=localhost,127.0.0.1
EXPIRE_MINS=30
ALGORITHM=HS256
```

## PostGIS

This project uses PostGIS for location-aware property search. PostGIS is a PostgreSQL extension that adds geographic types and indexes, so a property can store one real `location` point instead of separate text/number fields.

Enable it once in your database:

```sql
CREATE EXTENSION IF NOT EXISTS postgis;
```

The code stores coordinates in `location` fields with SRID `4326`, the standard GPS coordinate system used by latitude/longitude. When creating a point in Django, pass longitude first and latitude second:

```python
from django.contrib.gis.geos import Point

property.location = Point(longitude, latitude, srid=4326)
```

Example nearest-property query:

```python
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point

user_location = Point(longitude, latitude, srid=4326)

properties = (
    Property.objects
    .filter(status=Property.Status.AVAILABLE)
    .annotate(distance=Distance("location", user_location))
    .order_by("distance")
)
```

On Windows, GeoDjango also needs native GDAL installed and discoverable. If Django raises `Could not find the GDAL library`, install GDAL and set `GDAL_LIBRARY_PATH` if needed.

Uploaded property images are stored locally under `media/` in development.
The model uses Django's storage API, so the same `PropertyImage.image` field can later move to GCS by changing storage settings instead of changing the model.

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
