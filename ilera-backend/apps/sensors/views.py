from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from .serializers import SensorDataSerializer


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def post_sensor_data(request):
    serializer = SensorDataSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"status": "ok"}, status=201)
    return Response(serializer.errors, status=400)


from rest_framework import generics, permissions
from .models import SensorData
from .serializers import SensorDataSerializer


class SensorDataListCreateView(generics.ListCreateAPIView):
    queryset = SensorData.objects.all().select_related("device").order_by("-timestamp")
    serializer_class = SensorDataSerializer
    permission_classes = [permissions.AllowAny] 

    def get_queryset(self):
        """
        Optionally filter by ?device_id=XXXX
        """
        queryset = super().get_queryset()
        device_id = self.request.query_params.get("device_id")
        if device_id:
            queryset = queryset.filter(device__device_id=device_id)
        return queryset
