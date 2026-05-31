# properties/urls.py

from django.urls import path

from .views import (
    PropertyListView,
    PropertyDetailView,
    CreatePropertyView,
    UpdatePropertyView,
)

urlpatterns = [

    # List properties
    path(
        "",
        PropertyListView.as_view(),
        name="property-list",
    ),

    path(
        "update/<int:pk>/",
        UpdatePropertyView.as_view(),
        name="property-update",
    ),
    # Create property
    path(
        "create/",
        CreatePropertyView.as_view(),
        name="property-create",
    ),

    # Property detail
    path(
        "<int:pk>/",
        PropertyDetailView.as_view(),
        name="property-detail",
    ),
]
