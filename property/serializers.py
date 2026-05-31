# properties/serializers.py

from rest_framework import serializers

from accounts.serializers import ProfileSerializer

from colleges.models import College
from colleges.serializers import CollegeSerializer

from .models import (
    Property,
    PropertyImage,
)


# Property image serializer
class PropertyImageSerializer(serializers.ModelSerializer):

    # Full image URL
    image_url = serializers.SerializerMethodField()

    class Meta:

        model = PropertyImage

        fields = (
            "id",
            "image",
            "image_url",
            "alt_text",
            "is_primary",
            "sort_order",
        )

    # Generate full URL
    def get_image_url(self, obj):

        request = self.context.get("request")

        if obj.image and request:

            return request.build_absolute_uri(
                obj.image.url
            )

        return None


# Property read serializer
class PropertySerializer(serializers.ModelSerializer):

    # Owner details
    owner = ProfileSerializer(
        read_only=True
    )

    # Property images
    images = PropertyImageSerializer(
        many=True,
        read_only=True,
    )

    # Nearby colleges
    nearby_colleges = CollegeSerializer(
        many=True,
        read_only=True,
    )

    class Meta:

        model = Property

        fields = (

            # IDs
            "id",

            # Owner
            "owner",

            # Property info
            "title",
            "status",
            "description",

            # Pricing
            "rent",
            "deposit",

            # Address
            "address",
            "city",
            "state",
            "pincode",

            # Geo location
            "location",

            # Colleges
            "nearby_colleges",

            # Room info
            "bedrooms",
            "bathrooms",
            "area_sqft",

            # Availability
            "available_from",

            # Images
            "images",

            # Timestamps
            "created_at",
            "updated_at",
        )

        read_only_fields = (
            "id",
            "owner",
            "created_at",
            "updated_at",
        )


# Property create/update serializer
class CreatePropertySerializer(serializers.ModelSerializer):

    # Accept college IDs
    nearby_colleges = serializers.PrimaryKeyRelatedField(
        queryset=College.objects.all(),
        many=True,
        required=False,
    )

    class Meta:

        model = Property

        exclude = (
            "owner",
            "created_at",
            "updated_at",
        )

    # Create property
    def create(self, validated_data):

        colleges = validated_data.pop(
            "nearby_colleges",
            []
        )

        property_obj = Property.objects.create(
            owner=self.context["request"].user,
            **validated_data,
        )

        # Attach colleges
        property_obj.nearby_colleges.set(
            colleges
        )

        return property_obj