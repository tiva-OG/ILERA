from django.contrib import admin
from .models import SensorDevice, SensorData

admin.site.register(SensorDevice)
admin.site.register(SensorData)