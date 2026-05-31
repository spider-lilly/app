from django.contrib.gis.geos import Point
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import User
from college.models import College
from .models import Property


class PropertyApiTests(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username="owner",
            email="owner@example.com",
            password="StrongPass123",
            role=User.Role.OWNER,
        )
        self.other_owner = User.objects.create_user(
            username="other",
            email="other@example.com",
            password="StrongPass123",
            role=User.Role.OWNER,
        )
        self.student = User.objects.create_user(
            username="student",
            email="student@example.com",
            password="StrongPass123",
            role=User.Role.STUDENT,
        )
        self.college = College.objects.create(
            name="City College",
            address="Central road",
            location=Point(77.594566, 12.971599, srid=4326),
        )
        self.property = Property.objects.create(
            owner=self.owner,
            title="Near campus room",
            status=Property.Status.AVAILABLE,
            description="Clean room",
            rent="10000.00",
            deposit="20000.00",
            address="Main road",
            city="Bangalore",
            state="Karnataka",
            pincode="560001",
            location=Point(77.594566, 12.971599, srid=4326),
            bedrooms=1,
            bathrooms=1,
            area_sqft="500.00",
        )
        self.property.nearby_colleges.add(self.college)

    def test_property_list_supports_price_filter_and_pagination(self):
        response = self.client.get(
            reverse("property-list"),
            {
                "min_rent": "9000",
                "max_rent": "11000",
                "page": 1,
            },
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["page"], 1)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["title"], "Near campus room")

    def test_property_list_rejects_invalid_location_filter(self):
        response = self.client.get(
            reverse("property-list"),
            {
                "lat": "12.9",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_owner_can_create_property(self):
        self.client.force_authenticate(self.owner)

        response = self.client.post(
            reverse("property-create"),
            {
                "title": "Second room",
                "status": Property.Status.AVAILABLE,
                "description": "Fresh listing",
                "rent": "12000.00",
                "deposit": "22000.00",
                "address": "Second road",
                "city": "Bangalore",
                "state": "Karnataka",
                "pincode": "560002",
                "latitude": 12.98,
                "longitude": 77.60,
                "nearby_colleges": [self.college.id],
                "bedrooms": 1,
                "bathrooms": 1,
                "area_sqft": "450.00",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Property.objects.count(), 2)

    def test_student_cannot_create_property(self):
        self.client.force_authenticate(self.student)

        response = self.client.post(
            reverse("property-create"),
            {
                "title": "Blocked room",
                "rent": "12000.00",
                "deposit": "22000.00",
                "address": "Second road",
                "city": "Bangalore",
                "state": "Karnataka",
                "pincode": "560002",
                "latitude": 12.98,
                "longitude": 77.60,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_owner_can_update_own_property(self):
        self.client.force_authenticate(self.owner)

        response = self.client.patch(
            reverse("property-update", kwargs={"pk": self.property.id}),
            {
                "rent": "11500.00",
                "latitude": 13.0,
                "longitude": 78.0,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.property.refresh_from_db()
        self.assertEqual(str(self.property.rent), "11500.00")
        self.assertEqual(float(self.property.location.y), 13.0)

    def test_owner_cannot_update_another_owners_property(self):
        self.client.force_authenticate(self.other_owner)

        response = self.client.patch(
            reverse("property-update", kwargs={"pk": self.property.id}),
            {"rent": "11500.00"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
