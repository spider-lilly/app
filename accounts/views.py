from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import LoginSerializer, ProfileSerializer, RegisterSerializer


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


class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(build_token_response(user), status=status.HTTP_201_CREATED)


class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        return Response(build_token_response(serializer.validated_data["user"]))


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = ProfileSerializer(request.user)
        return Response(serializer.data)
