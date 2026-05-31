# accounts/views.py

import os
import requests
import urllib.parse

from django.shortcuts import redirect

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework_simplejwt.tokens import RefreshToken

from .models import User

from .serializers import (
    LoginSerializer,
    ProfileSerializer,
    RegisterSerializer,
)


# Generate JWT tokens
def build_token_response(user):

    refresh = RefreshToken.for_user(user)

    access = refresh.access_token

    access["sub"] = str(user.id)
    access["role"] = user.role

    return {
        "access_token": str(access),
        "refresh_token": str(refresh),
        "token_type": "bearer",
    }


# Register API
class RegisterView(APIView):

    def post(self, request):

        serializer = RegisterSerializer(
            data=request.data
        )

        serializer.is_valid(raise_exception=True)

        user = serializer.save()

        return Response(
            build_token_response(user),
            status=status.HTTP_201_CREATED,
        )


# Login API
class LoginView(APIView):

    def post(self, request):

        serializer = LoginSerializer(
            data=request.data,
            context={"request": request},
        )

        serializer.is_valid(raise_exception=True)

        return Response(
            build_token_response(
                serializer.validated_data["user"]
            )
        )


# Profile API
class ProfileView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        serializer = ProfileSerializer(
            request.user
        )

        return Response(serializer.data)


# Google login redirect
class GoogleLoginView(APIView):

    authentication_classes = []
    permission_classes = []

    def get(self, request):

        params = {
            "client_id": os.getenv("GOOGLE_CLIENT_ID"),

            "redirect_uri":
            "http://127.0.0.1:8000/api/accounts/google/callback/",

            "response_type": "code",

            "scope": "openid email profile",

            "access_type": "offline",

            "prompt": "select_account",
        }

        url = (
            "https://accounts.google.com/o/oauth2/v2/auth?"
            + urllib.parse.urlencode(params)
        )

        return redirect(url)


# Google callback
class GoogleCallbackView(APIView):

    authentication_classes = []
    permission_classes = []

    def get(self, request):

        code = request.GET.get("code")

        # Exchange code for token
        token_response = requests.post(
            "https://oauth2.googleapis.com/token",
            data={
                "code": code,

                "client_id":
                os.getenv("GOOGLE_CLIENT_ID"),

                "client_secret":
                os.getenv("GOOGLE_CLIENT_SECRET"),

                "redirect_uri":
                "http://127.0.0.1:8000/api/accounts/google/callback/",

                "grant_type":
                "authorization_code",
            },
        )

        token_data = token_response.json()

        access_token = token_data.get("access_token")

        # Fetch Google user info
        user_info_response = requests.get(
            "https://www.googleapis.com/oauth2/v1/userinfo",
            headers={
                "Authorization":
                f"Bearer {access_token}"
            },
        )

        user_info = user_info_response.json()

        email = user_info["email"]

        # Create user if not exists
        user, created = User.objects.get_or_create(
            email=email,

            defaults={
                "username":
                email.split("@")[0],
            },
        )

        refresh = RefreshToken.for_user(user)

        return Response({
            "access_token":
            str(refresh.access_token),

            "refresh_token":
            str(refresh),

            "user": {
                "email": user.email,
                "username": user.username,
            },
        })