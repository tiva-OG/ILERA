import requests
import random
import time
import uuid

BASE_URL = "http://localhost:8000/api/v1/sensors/"
DEVICE_ID = input("Please enter the device id: ")


def generate_reading():
    return {
        "device_id": DEVICE_ID,
        "temperature": round(random.uniform(36.0, 39.0), 1),
        "heart_rate": random.randint(60, 120),
        "blood_oxygen": random.randint(90, 100),
        "steps": random.randint(0, 5),
        "battery_level": random.randint(10, 100),
    }


while True:
    payload = generate_reading()

    try:
        response = requests.post(BASE_URL, json=payload)
        print(f"[Sent]: {payload} | [Status]: {response.status_code}")
    except Exception as e:
        print(f"[Error]: {e}")

    time.sleep(1) # send reading every 2 seconds
