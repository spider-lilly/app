from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.contrib.gis.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        STUDENT = "student", "Student"
        OWNER = "owner", "Owner"
        ADMIN = "admin", "Admin"

    email = models.EmailField(unique=True)
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.STUDENT,
    )
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.email


class College(models.Model):
    name = models.CharField(max_length=150)
    address = models.TextField(blank=True)
    location = models.PointField(geography=True, srid=4326)

    def __str__(self):
        return self.name


def property_image_upload_path(instance, filename):
    return f"properties/{instance.property_id}/images/{filename}"


class Property(models.Model):
    class Status(models.TextChoices):
        AVAILABLE = "available", "Available"
        RENTED = "rented", "Rented"
        DRAFT = "draft", "Draft"

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="properties",
    )
    title = models.CharField(max_length=155)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.AVAILABLE,
    )
    description = models.TextField(blank=True)

    rent = models.DecimalField(max_digits=10, decimal_places=2)
    deposit = models.DecimalField(max_digits=10, decimal_places=2)

    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=20)
    location = models.PointField(geography=True, srid=4326)

    nearby_colleges = models.ManyToManyField(
        College,
        related_name="nearby_properties",
        blank=True,
    )
    bedrooms = models.PositiveSmallIntegerField(default=1)
    bathrooms = models.PositiveSmallIntegerField(default=1)
    area_sqft = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    available_from = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["city"]),
            models.Index(fields=["state"]),
            models.Index(fields=["rent"]),
        ]

    def __str__(self):
        return self.title


class PropertyImage(models.Model):
    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name="images",
    )
    image = models.ImageField(upload_to=property_image_upload_path)
    alt_text = models.CharField(max_length=150, blank=True)
    is_primary = models.BooleanField(default=False)
    sort_order = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["sort_order", "id"]
        indexes = [
            models.Index(fields=["property", "is_primary"]),
        ]

    def __str__(self):
        return f"{self.property.title} image {self.id}"
