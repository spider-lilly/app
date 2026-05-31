from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class AuthApiTests(APITestCase):
    def test_register_returns_tokens(self):
        response = self.client.post(
            reverse("register"),
            {
                "username": "malik",
                "email": "malik@example.com",
                "password": "StrongPass123",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("access_token", response.data)
        self.assertIn("refresh_token", response.data)
        self.assertEqual(response.data["token_type"], "bearer")

    def test_login_and_profile(self):
        register_response = self.client.post(
            reverse("register"),
            {
                "username": "malik",
                "email": "malik@example.com",
                "password": "StrongPass123",
            },
            format="json",
        )

        login_response = self.client.post(
            reverse("login"),
            {
                "email": "malik@example.com",
                "password": "StrongPass123",
            },
            format="json",
        )

        self.assertEqual(login_response.status_code, status.HTTP_200_OK)

        token = login_response.data["access_token"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        profile_response = self.client.get(reverse("profile"))

        self.assertEqual(profile_response.status_code, status.HTTP_200_OK)
        self.assertEqual(profile_response.data["email"], "malik@example.com")
        self.assertEqual(profile_response.data["id"], register_response.data.get("id", profile_response.data["id"]))

    def test_public_registration_cannot_create_admin(self):
        response = self.client.post(
            reverse("register"),
            {
                "username": "adminish",
                "email": "adminish@example.com",
                "password": "StrongPass123",
                "role": "admin",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_profile_update_changes_current_user(self):
        self.client.post(
            reverse("register"),
            {
                "username": "malik",
                "email": "malik@example.com",
                "password": "StrongPass123",
            },
            format="json",
        )
        login_response = self.client.post(
            reverse("login"),
            {
                "email": "malik@example.com",
                "password": "StrongPass123",
            },
            format="json",
        )
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {login_response.data['access_token']}"
        )

        response = self.client.patch(
            reverse("profile-update"),
            {
                "username": "malik-updated",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "malik-updated")

    def test_change_password_requires_old_password(self):
        self.client.post(
            reverse("register"),
            {
                "username": "malik",
                "email": "malik@example.com",
                "password": "StrongPass123",
            },
            format="json",
        )
        login_response = self.client.post(
            reverse("login"),
            {
                "email": "malik@example.com",
                "password": "StrongPass123",
            },
            format="json",
        )
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {login_response.data['access_token']}"
        )

        response = self.client.post(
            reverse("change-password"),
            {
                "old_password": "wrong-password",
                "new_password": "NewStrongPass123",
                "confirm_password": "NewStrongPass123",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_logout_blacklists_refresh_token(self):
        self.client.post(
            reverse("register"),
            {
                "username": "malik",
                "email": "malik@example.com",
                "password": "StrongPass123",
            },
            format="json",
        )
        login_response = self.client.post(
            reverse("login"),
            {
                "email": "malik@example.com",
                "password": "StrongPass123",
            },
            format="json",
        )
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {login_response.data['access_token']}"
        )

        response = self.client.post(
            reverse("logout"),
            {
                "refresh_token": login_response.data["refresh_token"],
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
