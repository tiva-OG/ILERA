from django.urls import path
from .views import post_sensor_data

urlpatterns = [
    path("data/", post_sensor_data),
]
