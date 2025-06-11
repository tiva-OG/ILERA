from channels.routing import ProtocolTypeRouter, URLRouter
from itertools import chain

from apps.core.middleware import JWTAuthMiddlewareStack
from apps.notifications.routing import websocket_urlpatterns as notification_ws
from apps.sensors.routing import websocket_urlpatterns as sensor_ws


application = ProtocolTypeRouter(
    {
        "websocket": JWTAuthMiddlewareStack(URLRouter(list(chain(notification_ws, sensor_ws)))),
    }
)
