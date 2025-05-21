from rest_framework import serializers
from .models import SensorDevice, SensorData


class SensorDataSerializer(serializers.ModelSerializer):
    device_id = serializers.CharField(write_only=True)

    class Meta:
        model = SensorData
        fields = ["device_id", "temperature", "heart_rate", "blood_oxygen_level", "steps"]

    def create(self, validated_data):
        device_id = validated_data.pop("device_id")
        try:
            device = SensorDevice.objects.get(device_id=device_id)
        except SensorDevice.DoesNotExist:
            raise serializers.ValidationError("Unknown device ID")

        device.update_heartbeat()
        return SensorData.objects.create(device=device, **validated_data)
