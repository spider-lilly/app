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
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_REDIRECT_URI=http://127.0.0.1:8000/api/auth/google/callback/
GDAL_LIBRARY_PATH=C:\OSGeo4W\bin\gdal313.dll
GEOS_LIBRARY_PATH=C:\OSGeo4W\bin\geos_c.dll
ANON_THROTTLE_RATE=60/min
USER_THROTTLE_RATE=120/min
PROPERTY_LIST_THROTTLE_RATE=60/min
```

## PostGIS

This project uses PostGIS for location-aware property search. PostGIS is a PostgreSQL extension that adds geographic types and indexes, so a property can store one real `location` point instead of separate text/number fields.

Enable it once in your database:

```sql
CREATE EXTENSION IF NOT EXISTS postgis;
```

If tests or migrations fail with `extension "postgis" is not available`, the PostgreSQL server does not have PostGIS installed. Installing OSGeo4W fixes Django's local GDAL dependency, but the PostgreSQL server also needs the PostGIS extension package installed.

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

- `POST /api/auth/register/`
- `POST /api/auth/login/`
- `POST /api/auth/logout/`
- `GET /api/auth/profile/`
- `PATCH /api/auth/profile/update/`
- `POST /api/auth/change-password/`
- `GET /api/auth/google/`
- `GET /api/auth/google/callback/`
- `GET /api/colleges/`
- `PATCH /api/colleges/update/<id>/`
- `GET /api/properties/`
- `POST /api/properties/create/`
- `GET /api/properties/<id>/`
- `PATCH /api/properties/update/<id>/`

Authenticated requests use:

```http
Authorization: Bearer <access_token>
```

## Property Filters

`GET /api/properties/` supports:

- `city`
- `state`
- `pincode`
- `min_rent`
- `max_rent`
- `min_bedrooms`
- `max_bedrooms`
- `min_bathrooms`
- `max_bathrooms`
- `min_area`
- `max_area`
- `available_from`
- `college_id`
- `lat`
- `lng`
- `radius_km`
- `page`
- `page_size`

Examples:

```http
GET /api/properties/?city=Bangalore&min_rent=8000&max_rent=15000
GET /api/properties/?college_id=1&radius_km=3
GET /api/properties/?lat=12.971599&lng=77.594566&radius_km=5&page=2
```

Paginated responses include:

```json
{
  "count": 42,
  "next": "...?page=3",
  "previous": "...?page=1",
  "page": 2,
  "page_size": 10,
  "total_pages": 5,
  "results": []
}
```

## Updates

Use `PATCH` for partial updates.

Profile updates allow `username` and `email`; role changes are intentionally blocked through the public profile endpoint.

Property updates are restricted to authenticated users with the `owner` role who own the property.

College updates are restricted to Django staff/admin users.

For property and college locations, send latitude and longitude:

```json
{
  "latitude": 12.971599,
  "longitude": 77.594566
}
```

The API converts them to PostGIS points internally.

## Verification

```bash
python manage.py check
python manage.py test
```

`python manage.py test` requires the PostgreSQL server to have PostGIS installed because test databases also need the `postgis` extension.
