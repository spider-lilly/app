from django.contrib import admin
from django.urls import include, path
from rest_framework.decorators import api_view
from rest_framework.response import Response

from django.conf import settings


@api_view(["GET"])
def health_check(request):
    return Response(
        {
            "message": "API running",
            "debug": settings.DEBUG,
        }
    )


urlpatterns = [
    path("", health_check),
    path("admin/", admin.site.urls),
    path("api/auth/", include("accounts.urls")),
]
