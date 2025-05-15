from rest_framework import generics, permissions

from .models import Livestock
from .serializers import LivestockSerializer
from apps.core.permissions import IsFarmer, IsVeterinarian


class LivestockListCreateView(generics.ListCreateAPIView):
    serializer_class = LivestockSerializer
    permission_classes = [IsFarmer]

    def get_queryset(self):
        return Livestock.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        # serializer
        pass
