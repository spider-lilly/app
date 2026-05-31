# colleges/urls.py

from django.urls import path

from .views import CollegeListView


urlpatterns = [

    path(
        "",
        CollegeListView.as_view(),
    ),
]