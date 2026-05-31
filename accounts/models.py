# accounts/models.py

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):

    # User roles
    class Role(models.TextChoices):
        STUDENT = "student", "Student"
        OWNER = "owner", "Owner"
        ADMIN = "admin", "Admin"

    # Email login
    email = models.EmailField(unique=True)

    # User role
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.STUDENT,
    )

    # Login field
    USERNAME_FIELD = "email"

    # Required while creating superuser
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.email