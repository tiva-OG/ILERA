from rest_framework import generics, permissions
from rest_framework.response import Response

from .models import SensorReading
from .serializers import SensorReadingSerializer


class SensorReadingListCreateView(generics.ListCreateAPIView):
    serializer_class = SensorReadingSerializer

    def get_permissions(self):
        if self.request.method == "GET":
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def get_queryset(self):
        user = self.request.user
        device_id = self.request.query_params.get("device_id")

        queryset = SensorReading.objects.filter(device__device_id=device_id, device__livestock__owner=user).order_by("-timestamp")[:150]
        return queryset
