# properties/urls.py

from django.urls import path

from .views import (
    PropertyListView,
    PropertyDetailView,
    CreatePropertyView,
)

urlpatterns = [

    # List properties
    path(
        "",
        PropertyListView.as_view(),
    ),

    # Create property
    path(
        "create/",
        CreatePropertyView.as_view(),
    ),

    # Property detail
    path(
        "<int:pk>/",
        PropertyDetailView.as_view(),
    ),
]