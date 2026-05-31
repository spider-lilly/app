from datetime import timedelta
from pathlib import Path
import os

import dj_database_url
from dotenv import load_dotenv

from django.core.exceptions import ImproperlyConfigured


# =========================================================
# BASE / ENV
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")


# =========================================================
# GEODJANGO
# =========================================================

GDAL_LIBRARY_PATH = os.getenv("GDAL_LIBRARY_PATH")
GEOS_LIBRARY_PATH = os.getenv("GEOS_LIBRARY_PATH")

if os.name == "nt":

    osgeo_bin = Path(
        os.getenv("OSGEO4W_ROOT", "C:/OSGeo4W")
    ) / "bin"

    if osgeo_bin.exists():
        os.add_dll_directory(str(osgeo_bin))


# =========================================================
# HELPERS
# =========================================================

def env_bool(name, default=False):

    value = os.getenv(name)

    if value is None:
        return default

    return value.lower() in {
        "1", "true", "yes", "on"
    }


# =========================================================
# SECURITY
# =========================================================

DEBUG = env_bool("DEBUG", False)

SECRET_KEY = os.getenv("SECRET_KEY")

if not SECRET_KEY:

    if DEBUG:
        SECRET_KEY = "dev-only-change-me"

    else:
        raise ImproperlyConfigured(
            "SECRET_KEY must be set."
        )


ALLOWED_HOSTS = [

    host.strip()

    for host in os.getenv(
        "ALLOWED_HOSTS",
        "localhost,127.0.0.1"
    ).split(",")

    if host.strip()
]


# =========================================================
# APPS
# =========================================================

INSTALLED_APPS = [

    # Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.gis",
    "django.contrib.postgres",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Third-party
    "rest_framework",
    "rest_framework_simplejwt",

    # Local
    "accounts",
    "college",
    "property",
]


# =========================================================
# MIDDLEWARE
# =========================================================

MIDDLEWARE = [

    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


# =========================================================
# URLS / WSGI
# =========================================================

ROOT_URLCONF = "config.urls"

WSGI_APPLICATION = "config.wsgi.application"


# =========================================================
# TEMPLATES
# =========================================================

TEMPLATES = [
    {
        "BACKEND":
        "django.template.backends.django.DjangoTemplates",

        "DIRS": [],

        "APP_DIRS": True,

        "OPTIONS": {
            "context_processors": [

                "django.template.context_processors.request",

                "django.contrib.auth.context_processors.auth",

                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


# =========================================================
# DATABASE
# =========================================================

DATABASES = {
    "default": dj_database_url.config(
        default=os.getenv("DATABASE_URL", ""),
        conn_max_age=600,
    )
}

if not DATABASES["default"]:

    raise ImproperlyConfigured(
        "DATABASE_URL must be set."
    )


if DATABASES["default"]["ENGINE"] == (
    "django.db.backends.postgresql"
):

    DATABASES["default"]["ENGINE"] = (
        "django.contrib.gis.db.backends.postgis"
    )


if DATABASES["default"]["ENGINE"] != (
    "django.contrib.gis.db.backends.postgis"
):

    raise ImproperlyConfigured(
        "DATABASE_URL must point to PostGIS."
    )


# =========================================================
# AUTH
# =========================================================

AUTH_USER_MODEL = "accounts.User"


AUTH_PASSWORD_VALIDATORS = [

    {
        "NAME":
        "django.contrib.auth.password_validation."
        "UserAttributeSimilarityValidator",
    },

    {
        "NAME":
        "django.contrib.auth.password_validation."
        "MinimumLengthValidator",
    },

    {
        "NAME":
        "django.contrib.auth.password_validation."
        "CommonPasswordValidator",
    },

    {
        "NAME":
        "django.contrib.auth.password_validation."
        "NumericPasswordValidator",
    },
]


# =========================================================
# INTERNATIONALIZATION
# =========================================================

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# =========================================================
# STATIC / MEDIA
# =========================================================

STATIC_URL = "static/"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"


# =========================================================
# DEFAULT PK
# =========================================================

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# =========================================================
# DJANGO REST FRAMEWORK
# =========================================================

REST_FRAMEWORK = {

    "DEFAULT_AUTHENTICATION_CLASSES": (

        "rest_framework_simplejwt.authentication."
        "JWTAuthentication",
    ),

    "DEFAULT_PERMISSION_CLASSES": (

        "rest_framework.permissions.AllowAny",
    ),
}


# =========================================================
# SIMPLE JWT
# =========================================================

SIMPLE_JWT = {

    "ACCESS_TOKEN_LIFETIME":
    timedelta(
        minutes=int(
            os.getenv("EXPIRE_MINS", "30")
        )
    ),

    "REFRESH_TOKEN_LIFETIME":
    timedelta(days=7),

    "AUTH_HEADER_TYPES":
    ("Bearer",),

    "ALGORITHM":
    os.getenv("ALGORITHM", "HS256"),

    "SIGNING_KEY":
    SECRET_KEY,

    "USER_ID_FIELD":
    "id",

    "USER_ID_CLAIM":
    "user_id",
}