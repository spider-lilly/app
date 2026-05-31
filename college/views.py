# colleges/views.py

from rest_framework.generics import ListAPIView

from .models import College
from .serializers import CollegeSerializer


# List all colleges
class CollegeListView(ListAPIView):

    queryset = College.objects.all()

    serializer_class = CollegeSerializer