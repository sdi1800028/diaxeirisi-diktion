import paho.mqtt.client as mqtt
import json
import time
import logging
import sys
import random

# --- Logging Setup ---
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# --- MQTT Config ---
broker = "localhost"
port = 1883
topic = "drones/llm"
dataset_file = "drone_dataset.jsonl"
delay_between_messages = 0.1  # seconds
max_messages = None  # ή π.χ. 50 για δοκιμές

# --- Δημιουργία MQTT Client ---
client = mqtt.Client(client_id=f"drone_publisher_{random.randint(1000,9999)}")

try:
    client.connect(broker, port, 60)
    logging.info(f"Connected to MQTT broker at {broker}:{port}")
except Exception as e:
    logging.critical(f"Could not connect to MQTT broker: {e}")
    sys.exit(1)

# --- Ανάγνωση και αποστολή δεδομένων ---
try:
    with open(dataset_file, "r") as f:
        for line_num, line in enumerate(f, start=1):
            if max_messages and line_num > max_messages:
                break

            try:
                message = json.loads(line.strip())
                payload = json.dumps(message)

                result = client.publish(topic, payload)
                status = result.rc

                if status == mqtt.MQTT_ERR_SUCCESS:
                    logging.info(f"[{line_num}] Sent: {payload}")
                else:
                    logging.warning(f"[{line_num}] Failed to publish message (code {status})")

                time.sleep(delay_between_messages)
            except json.JSONDecodeError as e:
                logging.warning(f"[{line_num}] Skipped invalid JSON: {e}")
except FileNotFoundError:
    logging.critical(f"Dataset file not found: {dataset_file}")
    sys.exit(1)
except Exception as e:
    logging.error(f"Unexpected error: {e}", exc_info=True)
finally:
    client.disconnect()
    logging.info("Disconnected from broker.")
