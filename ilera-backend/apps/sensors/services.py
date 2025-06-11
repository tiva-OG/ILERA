from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from .serializers import SensorReadingSerializer


class SensorService:

    @classmethod
    def send(cls, reading):
        channel_layer = get_channel_layer()
        group_name = f"device_{reading.device.device_id}"

        payload = SensorReadingSerializer(reading).data

        async_to_sync(channel_layer.group_send)(
            group_name,
            {"type": "send.reading", "reading": payload},
        )
