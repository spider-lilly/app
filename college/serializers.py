# colleges/serializers.py

from rest_framework import serializers
from django.contrib.gis.geos import Point

from .models import College


class CollegeSerializer(serializers.ModelSerializer):
    location = serializers.SerializerMethodField()
    latitude = serializers.FloatField(write_only=True, required=False)
    longitude = serializers.FloatField(write_only=True, required=False)

    class Meta:
        model = College

        fields = (
            "id",
            "name",
            "address",
            "location",
            "latitude",
            "longitude",
        )

    def get_location(self, obj):
        if not obj.location:
            return None

        return {
            "latitude": obj.location.y,
            "longitude": obj.location.x,
        }

    def validate(self, attrs):
        latitude = attrs.get("latitude")
        longitude = attrs.get("longitude")

        if (latitude is None) ^ (longitude is None):
            raise serializers.ValidationError(
                "Both latitude and longitude are required together."
            )

        if latitude is not None and not -90 <= latitude <= 90:
            raise serializers.ValidationError(
                {"latitude": "Latitude must be between -90 and 90."}
            )

        if longitude is not None and not -180 <= longitude <= 180:
            raise serializers.ValidationError(
                {"longitude": "Longitude must be between -180 and 180."}
            )

        return attrs

    def create(self, validated_data):
        latitude = validated_data.pop("latitude", None)
        longitude = validated_data.pop("longitude", None)

        if latitude is not None and longitude is not None:
            validated_data["location"] = Point(
                longitude,
                latitude,
                srid=4326,
            )

        return super().create(validated_data)

    def update(self, instance, validated_data):
        latitude = validated_data.pop("latitude", None)
        longitude = validated_data.pop("longitude", None)

        if latitude is not None and longitude is not None:
            instance.location = Point(
                longitude,
                latitude,
                srid=4326,
            )

        return super().update(instance, validated_data)
