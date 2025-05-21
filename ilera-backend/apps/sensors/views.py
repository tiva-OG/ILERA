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
