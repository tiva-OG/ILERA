from django.db import models
from django.utils import timezone

from apps.core.models import ULIDModel
from apps.livestock.models import Livestock


class SensorDevice(ULIDModel):
    device_id = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=100, blank=True)
    livestock = models.OneToOneField(Livestock, on_delete=models.CASCADE, related_name="sensor_device")
    is_active = models.BooleanField(default=True)
    last_heartbeat = models.DateTimeField(null=True, blank=True)

    def update_heartbeat(self):
        self.last_heartbeat = timezone.now()
        self.save()

    def __str__(self):
        return f"{self.device_id} - {self.livestock.get_fullname()}"


class SensorData(ULIDModel):
    device = models.ForeignKey(SensorDevice, on_delete=models.CASCADE)
    temperature = models.FloatField(blank=True, null=True)
    heart_rate = models.IntegerField(blank=True, null=True)
    blood_oxygen_level = models.IntegerField(blank=True, null=True)
    steps = models.IntegerField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Data from {self.device.device_id} @ {self.timestamp}"
