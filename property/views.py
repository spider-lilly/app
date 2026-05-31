

# Create your views here.
# properties/views.py

from rest_framework.permissions import (
    IsAuthenticated,
)
from django.contrib.gis.measure import D
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point
from rest_framework.generics import (
    ListAPIView,
    RetrieveAPIView,
    CreateAPIView,
    UpdateAPIView,
)
from rest_framework.throttling import ScopedRateThrottle
from property.pagination import CustomPagination

from .permissions import IsOwner , IsPropertyOwner
from college.models import College
from .models import Property

from .serializers import (
    PropertySerializer,
    CreatePropertySerializer,
    PropertyFilterSerializer,
)


# List all available properties
class PropertyListView(ListAPIView):
    serializer_class = PropertySerializer
    pagination_class = CustomPagination
    throttle_classes= [ScopedRateThrottle]
    throttle_scope = "property_list"

    def get_queryset(self):
        queryset=(
            Property.objects.filter(status=Property.Status.AVAILABLE)
            .select_related('owner').prefetch_related('images','nearby_colleges')
        )

        serializer = PropertyFilterSerializer(
            data=self.request.query_params
        )
        serializer.is_valid(raise_exception=True)
        params = serializer.validated_data

        if params.get('city'):
            queryset=queryset.filter(city__iexact=params['city'])
        if params.get('state'):
            queryset=queryset.filter(state__iexact=params['state'])
        if params.get('pincode'):
            queryset=queryset.filter(pincode__iexact=params['pincode'])
        if params.get('min_rent') is not None:
            queryset=queryset.filter(rent__gte=params['min_rent'])
        if params.get('max_rent') is not None:
            queryset=queryset.filter(rent__lte=params['max_rent'])
        if params.get('min_bedrooms') is not None:
            queryset=queryset.filter(bedrooms__gte=params['min_bedrooms'])
        if params.get('max_bedrooms') is not None:
            queryset=queryset.filter(bedrooms__lte=params['max_bedrooms'])
        if params.get('min_bathrooms') is not None:
            queryset=queryset.filter(bathrooms__gte=params['min_bathrooms'])
        if params.get('max_bathrooms') is not None:
            queryset=queryset.filter(bathrooms__lte=params['max_bathrooms'])
        if params.get('available_from'):
            queryset=queryset.filter(available_from__lte=params['available_from'])
        if params.get('min_area') is not None:
            queryset=queryset.filter(area_sqft__gte=params['min_area'])
        if params.get('max_area') is not None:
            queryset=queryset.filter(area_sqft__lte=params['max_area'])
        center=None
        if params.get('college_id'):
            college=College.objects.filter(id=params['college_id']).first()
            if college and college.location:
                center=college.location
                queryset=queryset.filter(nearby_colleges=college)
        elif params.get('lat') and params.get('lng'):
            center=Point(params['lng'], params['lat'], srid=4326)
        if center:
            queryset=queryset.annotate(distance=Distance('location',center)).order_by('distance','-created_at')
            if params.get('radius_km'):
                queryset=queryset.filter(location__distance_lte=(center,D(km=params['radius_km'])))
        else:
            queryset=queryset.order_by('-created_at')
        return queryset.distinct()
    

# Property detail
class PropertyDetailView(RetrieveAPIView):

    queryset = Property.objects.select_related(
        "owner"
    ).prefetch_related(
        "images",
        "nearby_colleges",
    )

    serializer_class = PropertySerializer


# Create property
class CreatePropertyView(CreateAPIView):

    serializer_class = CreatePropertySerializer

    permission_classes = [
        IsAuthenticated,
        IsOwner,
    ]

    def perform_create(self, serializer):

        serializer.save()

class UpdatePropertyView(UpdateAPIView):
    serializer_class=CreatePropertySerializer
    permission_classes=[
        IsAuthenticated,
        IsOwner,
        IsPropertyOwner,
    ]
    http_method_names = ["patch", "put"]
    def get_queryset(self):
        return Property.objects.filter(
            owner=self.request.user
        )
