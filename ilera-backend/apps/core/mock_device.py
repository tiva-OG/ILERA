import requests
import time
import random

from apps.livestock.models import Livestock
from apps.sensors.models import SensorDevice, SensorReading

BASE_URL = "http://localhost:8000/api/v1/sensors/"


def generate_reading(device_id):
    return {
        "device_id": device_id,
        "temperature": round(random.uniform(36.0, 39.0), 1),
        "heart_rate": random.randint(60, 100),
        "blood_oxygen": random.randint(90, 100),
        "steps": random.randint(0, 5),
        "battery_level": random.randint(20, 100),
    }

    return {
        "device_id": device_id,
        "temperature": round(random.uniform(36.0, 39.0), 1),
        "heart_rate": random.randint(60, 120),
        "blood_oxygen": random.randint(90, 100),
        "steps": random.randint(0, 5),
        "battery_level": random.randint(10, 100),
    }


def mock_loop():
    while True:
        for animal in Livestock.objects.filter(is_test=True):
            device = SensorDevice(livestock=animal)
            payload = generate_reading(device.id)
            response = requests.post(BASE_URL, json=payload)

            print(f"[Sent]: {payload} | [Status]: {response.status_code}")

        time.sleep(1)  # send reading every 2 seconds
