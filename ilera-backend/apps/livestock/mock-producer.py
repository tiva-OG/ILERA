import asyncio
import json
from datetime import datetime, timezone
from random import randint, uniform

from channels.layers import get_channel_layer
from django.apps import apps

from apps.livestock.models import Livestock
from apps.sensors.models import SensorDevice, SensorReading

Livestock = apps.get_model("livestock", "Livestock")
SensorReading = apps.get_model("livestock", "SensorReading")


# realistic ranges
def make_payload(livestock):
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "temperature": round(uniform(37.5, 39.5), 1),
        "heart_rate": randint(60, 95),
        "blood_oxygen": randint(94, 99),
        "steps": randint(0, 4),
        "battery_level": randint(25, 100),
    }


async def mock_loop():
    channel_layer = get_channel_layer()
    while True:
        # grab every test animal
        for animal in Livestock.objects.filter(is_test=True):
            data = make_payload(animal)

            # 1️⃣  Persist to DB  (so history API & offline cache work)
            SensorReading.objects.create(livestock=animal, **data)

            # 2️⃣  Push over websocket
            await channel_layer.group_send(
                f"livestock_{animal.device_id}",
                {
                    "type": "send_sensor_data",  # handled by your consumer
                    "data": json.dumps(data),
                },
            )

        await asyncio.sleep(8)  # 8‑second cadence is demo‑friendly
