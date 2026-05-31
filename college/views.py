# colleges/views.py

from rest_framework.generics import ListAPIView, UpdateAPIView
from rest_framework.permissions import IsAdminUser

from .models import College
from .serializers import CollegeSerializer


# List all colleges
class CollegeListView(ListAPIView):

    queryset = College.objects.all()

    serializer_class = CollegeSerializer

class CollegeUpdateView(UpdateAPIView):
    queryset = College.objects.all()
    serializer_class = CollegeSerializer
    permission_classes = [IsAdminUser]
    http_method_names = ["patch", "put"]