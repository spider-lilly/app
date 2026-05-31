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
from rest_framework_simplejwt.exceptions import TokenError

from .models import User

from .serializers import (
    LoginSerializer,
    ProfileSerializer,
    ProfileUpdateSerializer,
    ChangePasswordSerializer,
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

class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"detail": "Password changed successfully."},
            status=status.HTTP_200_OK,
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

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh_token")
        if refresh_token is None:
            return Response(
                {"error": "Refresh token is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except TokenError:
            return Response(
                {"error": "Invalid refresh token."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(status=status.HTTP_204_NO_CONTENT)



# Profile API
class ProfileView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        serializer = ProfileSerializer(
            request.user
        )

        return Response(serializer.data)

class ProfileUpdateView(APIView):

    permission_classes = [IsAuthenticated]

    def patch(self, request):

        serializer = ProfileUpdateSerializer(
            request.user,
            data=request.data,
            partial=True,
            context={"request": request},
        )

        serializer.is_valid(raise_exception=True)

        serializer.save()

        return Response(serializer.data)

# Google login redirect
class GoogleLoginView(APIView):

    authentication_classes = []
    permission_classes = []

    def get(self, request):
        client_id = os.getenv("GOOGLE_CLIENT_ID")

        if not client_id:
            return Response(
                {"detail": "Google OAuth is not configured."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        redirect_uri = os.getenv(
            "GOOGLE_REDIRECT_URI",
            "http://127.0.0.1:8000/api/auth/google/callback/",
        )

        params = {
            "client_id": client_id,

            "redirect_uri":
            redirect_uri,

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

        if not code:
            return Response(
                {"detail": "Google authorization code is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        client_id = os.getenv("GOOGLE_CLIENT_ID")
        client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
        redirect_uri = os.getenv(
            "GOOGLE_REDIRECT_URI",
            "http://127.0.0.1:8000/api/auth/google/callback/",
        )

        if not client_id or not client_secret:
            return Response(
                {"detail": "Google OAuth is not configured."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        # Exchange code for token
        try:
            token_response = requests.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "code": code,
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "redirect_uri": redirect_uri,
                    "grant_type": "authorization_code",
                },
                timeout=10,
            )
            token_response.raise_for_status()
        except requests.RequestException:
            return Response(
                {"detail": "Could not exchange Google authorization code."},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        token_data = token_response.json()

        access_token = token_data.get("access_token")

        if not access_token:
            return Response(
                {"detail": "Google did not return an access token."},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        # Fetch Google user info
        try:
            user_info_response = requests.get(
                "https://www.googleapis.com/oauth2/v1/userinfo",
                headers={
                    "Authorization":
                    f"Bearer {access_token}"
                },
                timeout=10,
            )
            user_info_response.raise_for_status()
        except requests.RequestException:
            return Response(
                {"detail": "Could not fetch Google user profile."},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        user_info = user_info_response.json()

        email = user_info.get("email")

        if not email:
            return Response(
                {"detail": "Google profile did not include an email."},
                status=status.HTTP_502_BAD_GATEWAY,
            )

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
