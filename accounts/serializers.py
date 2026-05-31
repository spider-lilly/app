# accounts/serializers.py

from django.contrib.auth import authenticate
from rest_framework import serializers

from .models import User


# JWT response serializer
class TokenResponseSerializer(serializers.Serializer):
    access_token = serializers.CharField()
    refresh_token = serializers.CharField()
    token_type = serializers.CharField(default="bearer")


# User registration
class RegisterSerializer(serializers.ModelSerializer):

    password = serializers.CharField(
        write_only=True,
        min_length=8,
    )

    class Meta:
        model = User

        fields = (
            "id",
            "username",
            "email",
            "password",
            "role",
        )

        read_only_fields = ("id",)

    # Prevent admin registration
    def validate_role(self, value):

        if value == User.Role.ADMIN:
            raise serializers.ValidationError(
                "Admin users cannot be created publicly."
            )

        return value

    # Create user
    def create(self, validated_data):

        password = validated_data.pop("password")

        user = User(**validated_data)

        user.set_password(password)

        user.save()

        return user


# Login serializer
class LoginSerializer(serializers.Serializer):

    email = serializers.EmailField()

    password = serializers.CharField(
        write_only=True
    )

    def validate(self, attrs):

        request = self.context.get("request")

        user = authenticate(
            request=request,
            username=attrs["email"],
            password=attrs["password"],
        )

        if not user:
            raise serializers.ValidationError(
                "Invalid credentials."
            )

        if not user.is_active:
            raise serializers.ValidationError(
                "This account is disabled."
            )

        attrs["user"] = user

        return attrs


# User profile serializer
class ProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = User

        fields = (
            "id",
            "email",
            "username",
            "role",
        )