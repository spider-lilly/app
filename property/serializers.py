# properties/serializers.py

from rest_framework import serializers
from django.contrib.gis.geos import Point

from accounts.serializers import ProfileSerializer

from college.models import College
from college.serializers import CollegeSerializer

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
    distance_km=serializers.SerializerMethodField()
    location = serializers.SerializerMethodField()
    latitude = serializers.SerializerMethodField()
    longitude = serializers.SerializerMethodField()

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
            "latitude",
            "longitude",
            "distance_km",

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
    
    def get_distance_km(self,obj):
        distance=getattr(obj,'distance',None)
        if distance is None:
            return None
        return round(distance.km,2)

    def get_location(self, obj):
        if not obj.location:
            return None

        return {
            "latitude": obj.location.y,
            "longitude": obj.location.x,
        }

    def get_latitude(self, obj):
        return obj.location.y if obj.location else None

    def get_longitude(self, obj):
        return obj.location.x if obj.location else None


# Property create/update serializer
class CreatePropertySerializer(serializers.ModelSerializer):

    # Accept college IDs
    nearby_colleges = serializers.PrimaryKeyRelatedField(
        queryset=College.objects.all(),
        many=True,
        required=False,
    )
    latitude = serializers.FloatField(write_only=True)
    longitude = serializers.FloatField(write_only=True)

    class Meta:

        model = Property

        exclude = (
            "owner",
            "location",
            "created_at",
            "updated_at",
        )

    def validate(self, attrs):
        latitude = attrs.get("latitude")
        longitude = attrs.get("longitude")

        if latitude is not None and not -90 <= latitude <= 90:
            raise serializers.ValidationError(
                {"latitude": "Latitude must be between -90 and 90."}
            )

        if longitude is not None and not -180 <= longitude <= 180:
            raise serializers.ValidationError(
                {"longitude": "Longitude must be between -180 and 180."}
            )

        return attrs

    # Create property
    def create(self, validated_data):

        colleges = validated_data.pop(
            "nearby_colleges",
            []
        )
        latitude = validated_data.pop("latitude")
        longitude = validated_data.pop("longitude")

        property_obj = Property.objects.create(
            owner=self.context["request"].user,
            location=Point(longitude, latitude, srid=4326),
            **validated_data,
        )

        # Attach colleges
        property_obj.nearby_colleges.set(
            colleges
        )

        return property_obj
    
    def update(self,instance,validated_data):
        colleges = validated_data.pop(
            "nearby_colleges",
            None
        )
        latitude = validated_data.pop("latitude", None)
        longitude = validated_data.pop("longitude", None)

        if (latitude is None) ^ (longitude is None):
            raise serializers.ValidationError(
                "Both latitude and longitude are required to update location."
            )

        for attr,value in validated_data.items():
            setattr(instance,attr,value)

        if latitude is not None and longitude is not None:
            instance.location = Point(longitude, latitude, srid=4326)

        if colleges is not None:
            instance.nearby_colleges.set(colleges)
        instance.save()
        return instance


class PropertyFilterSerializer(serializers.Serializer):
    city = serializers.CharField(required=False, allow_blank=False)
    state = serializers.CharField(required=False, allow_blank=False)
    pincode = serializers.CharField(required=False, allow_blank=False)
    min_rent = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    max_rent = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    min_bedrooms = serializers.IntegerField(min_value=0, required=False)
    max_bedrooms = serializers.IntegerField(min_value=0, required=False)
    min_bathrooms = serializers.IntegerField(min_value=0, required=False)
    max_bathrooms = serializers.IntegerField(min_value=0, required=False)
    available_from = serializers.DateField(required=False)
    min_area = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    max_area = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    college_id = serializers.IntegerField(min_value=1, required=False)
    lat = serializers.FloatField(required=False)
    lng = serializers.FloatField(required=False)
    radius_km = serializers.FloatField(min_value=0, required=False)

    def validate(self, attrs):
        if "lat" in attrs or "lng" in attrs:
            if "lat" not in attrs or "lng" not in attrs:
                raise serializers.ValidationError(
                    "Both lat and lng are required for location search."
                )

        if "lat" in attrs and not -90 <= attrs["lat"] <= 90:
            raise serializers.ValidationError(
                {"lat": "Latitude must be between -90 and 90."}
            )

        if "lng" in attrs and not -180 <= attrs["lng"] <= 180:
            raise serializers.ValidationError(
                {"lng": "Longitude must be between -180 and 180."}
            )

        if attrs.get("min_rent") and attrs.get("max_rent"):
            if attrs["min_rent"] > attrs["max_rent"]:
                raise serializers.ValidationError(
                    "min_rent cannot be greater than max_rent."
                )

        if attrs.get("min_area") and attrs.get("max_area"):
            if attrs["min_area"] > attrs["max_area"]:
                raise serializers.ValidationError(
                    "min_area cannot be greater than max_area."
                )

        return attrs


