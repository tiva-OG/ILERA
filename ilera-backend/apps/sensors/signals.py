from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import SensorReading
from .services import SensorService


@receiver(post_save, sender=SensorReading)
def sensor_reading_handler(sender, instance, **kwargs):
    SensorService.send(instance)
