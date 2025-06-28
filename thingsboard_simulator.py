import json
import time
import random
import requests
import logging

logging.basicConfig(level=logging.INFO)

ACCESS_TOKEN = "DEVICE_TOKEN" # άλλαξε το με το πραγματικό token

THINGSBOARD_HOST = "http://localhost:8080"
url = f"{THINGSBOARD_HOST}/api/v1/{ACCESS_TOKEN}/telemetry"

headers = {'Content-Type': 'application/json'}

while True:
    telemetry = {
        "battery": random.randint(20, 100),
        "status": random.choice(["idle", "flying", "returning"]),
        "available": random.choice([True, False]),
        "payload_weight": round(random.uniform(0.0, 5.0), 2)
    }

    try:
        response = requests.post(url, data=json.dumps(telemetry), headers=headers)
        if response.status_code == 200:
            logging.info("Sent telemetry: %s", telemetry)
        else:
            logging.warning("Failed to send telemetry. Code: %s", response.status_code)

    except requests.RequestException as e:
        logging.error("Connection to ThingsBoard failed: %s", e)

    time.sleep(5)
