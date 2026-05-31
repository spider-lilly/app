# colleges/urls.py

from django.urls import path

from .views import CollegeListView, CollegeUpdateView


urlpatterns = [

    path(
        "",
        CollegeListView.as_view(),
        name="college-list",
    ),
    path(
        "update/<int:pk>/",
        CollegeUpdateView.as_view(),
        name="college-update",
    ),
]
