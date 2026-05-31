# colleges/models.py

from django.contrib.gis.db import models


class College(models.Model):

    # College name
    name = models.CharField(
        max_length=150
    )

    # Full address
    address = models.TextField(
        blank=True
    )

    # Geo location
    location = models.PointField(
        geography=True,
        srid=4326,
    )

    def __str__(self):
        return self.name