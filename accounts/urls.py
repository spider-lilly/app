# accounts/urls.py

from django.urls import path

from .views import (
    RegisterView,
    LoginView,
    ProfileView,
    GoogleLoginView,
    GoogleCallbackView,
)

urlpatterns = [

    path(
        "register/",
        RegisterView.as_view(),
    ),

    path(
        "login/",
        LoginView.as_view(),
    ),

    path(
        "profile/",
        ProfileView.as_view(),
    ),

    path(
        "google/",
        GoogleLoginView.as_view(),
    ),

    path(
        "google/callback/",
        GoogleCallbackView.as_view(),
    ),
]