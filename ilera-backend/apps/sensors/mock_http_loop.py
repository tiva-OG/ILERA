# apps/sensors/mock_http_loop.py
import os
import time
import random
import requests
from django.utils import timezone
from apps.livestock.models import Livestock
from apps.sensors.models import SensorDevice

BASE_URL = os.getenv("SENSOR_POST_URL", "http://localhost:8000/api/v1/sensors/")
POST_INTERVAL = float(os.getenv("MOCK_POST_EVERY", "2"))  # seconds
AUTH_TOKEN = os.getenv("API_TOKEN")  # optional

HEADERS = {"Authorization": f"Token {AUTH_TOKEN}"} if AUTH_TOKEN else {}


def generate_reading(device_id: str) -> dict:
    """Return a realistic mock payload for one sensor device."""
    return {
        "device_id": device_id,
        # "timestamp": timezone.now().isoformat(),
        "temperature": round(random.uniform(36.0, 39.0), 1),
        "heart_rate": random.randint(60, 100),
        "blood_oxygen": random.randint(90, 100),
        "steps": random.randint(0, 6),
        "battery_level": random.randint(30, 100),
    }


def run_forever() -> None:
    """Infinite loop that posts to your existing endpoint."""
    print("[MockLoop] 🔄 starting up…")
    while True:
        for animal in Livestock.objects.filter(is_test=True):
            device = SensorDevice.objects.get(livestock=animal)
            payload = generate_reading(device.device_id)
            print("PAYLOAD:", payload)
            try:
                r = requests.post(BASE_URL, json=payload)
                print(f"[MockLoop] ✅ {r.status_code} — {payload}")
            except Exception as exc:
                # network hiccups, endpoint down, etc.
                print(f"[MockLoop] ❌ POST failed: {exc}")

        time.sleep(POST_INTERVAL)
