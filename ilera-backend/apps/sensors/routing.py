from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    # re_path(r"ws/notifications/?$", consumers.NotificationConsumer.as_asgi()),
    re_path(r"ws/sensors/(?P<device_id>[\w-]+)/?$", consumers.SensorConsumer.as_asgi()),
]
