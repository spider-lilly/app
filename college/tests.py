from django.contrib.gis.geos import Point
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import User
from .models import College


class CollegeApiTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username="admin",
            email="admin@example.com",
            password="StrongPass123",
            is_staff=True,
        )
        self.student = User.objects.create_user(
            username="student",
            email="student@example.com",
            password="StrongPass123",
        )
        self.college = College.objects.create(
            name="City College",
            address="Central road",
            location=Point(77.594566, 12.971599, srid=4326),
        )

    def test_list_colleges_is_public(self):
        response = self.client.get(reverse("college-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["name"], "City College")

    def test_non_admin_cannot_update_college(self):
        self.client.force_authenticate(self.student)

        response = self.client.patch(
            reverse("college-update", kwargs={"pk": self.college.id}),
            {"name": "Blocked College"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_update_college_location(self):
        self.client.force_authenticate(self.admin)

        response = self.client.patch(
            reverse("college-update", kwargs={"pk": self.college.id}),
            {
                "name": "Updated College",
                "latitude": 13.0,
                "longitude": 78.0,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Updated College")
        self.college.refresh_from_db()
        self.assertEqual(float(self.college.location.y), 13.0)
        self.assertEqual(float(self.college.location.x), 78.0)
