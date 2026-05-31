# accounts/urls.py

from django.urls import path

from .views import (
    RegisterView,
    ChangePasswordView,
    LoginView,
    LogoutView,
    ProfileView,
    ProfileUpdateView,
    GoogleLoginView,
    GoogleCallbackView,
)

urlpatterns = [

    path(
        "register/",
        RegisterView.as_view(),
        name="register",
    ),
    path(
        "change-password/",
        ChangePasswordView.as_view(),
        name="change-password",
    ),
    path(
        "login/",
        LoginView.as_view(),
        name="login",
    ),
    path(
        "logout/",
        LogoutView.as_view(),
        name="logout",
    ),

    path(
        "profile/",
        ProfileView.as_view(),
        name="profile",
    ),

    path(
        "profile/update/",
        ProfileUpdateView.as_view(),
        name="profile-update",
    ),
    path(
        "google/",
        GoogleLoginView.as_view(),
        name="google-login",
    ),

    path(
        "google/callback/",
        GoogleCallbackView.as_view(),
        name="google-callback",
    ),
]
