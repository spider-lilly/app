from django.shortcuts import render

# Create your views here.
# properties/views.py

from rest_framework.permissions import (
    IsAuthenticated,
)

from rest_framework.generics import (
    ListAPIView,
    RetrieveAPIView,
    CreateAPIView,
)

from .permissions import IsOwner

from .models import Property

from .serializers import (
    PropertySerializer,
    CreatePropertySerializer,
)


# List all available properties
class PropertyListView(ListAPIView):

    queryset = Property.objects.filter(
        status=Property.Status.AVAILABLE
    ).select_related(
        "owner"
    ).prefetch_related(
        "images",
        "nearby_colleges",
    )

    serializer_class = PropertySerializer


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