from django.urls import path
from .views import GoogleLoginView, GoogleCallbackView
from .views import LoginView, ProfileView, RegisterView


urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("google/login/", GoogleLoginView.as_view(), name="google-login"),
    path("google/callback/", GoogleCallbackView.as_view(), name="google-callback"),
    path("Login/", LoginView.as_view(), name="login-compat"),
    path("profile/", ProfileView.as_view(), name="profile"),
]
