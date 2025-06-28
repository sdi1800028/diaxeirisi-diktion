import json
import time
import logging
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
from llm_model import DroneLLM


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


broker = "localhost"
port = 1883
input_topic = "drones/llm"
output_topic = "drones/llm/response"

TB_BROKER = "thingsboard.local"  # ή IP, π.χ. 192.168.1.50
TB_PORT = 1883
TB_ACCESS_TOKEN = "EVICE_ACCESS_TOKEN"  # άλλαξε το με το πραγματικό token


llm = DroneLLM()

def send_to_thingsboard(drone_id, response_text):
    payload = {
        "drone_id": drone_id,
        "llm_response": response_text
    }
    try:
        publish.single(
            topic="v1/devices/me/telemetry",
            payload=json.dumps(payload),
            hostname=TB_BROKER,
            port=TB_PORT,
            auth={'username': TB_ACCESS_TOKEN}
        )
        logging.info(f"Sent LLM response to ThingsBoard for {drone_id}")
    except Exception as e:
        logging.error(f"Failed to publish to ThingsBoard: {e}")

def on_message(client, userdata, msg):
    try:
        payload_str = msg.payload.decode('utf-8')
        data = json.loads(payload_str)

        drone_id = data.get("drone_id", "Unknown")
        message = data.get("message")

        if not message:
            logging.warning(f"Received message with no 'message' field from {drone_id}. Ignored.")
            return

        logging.info(f"Received from {drone_id}: {message}")

        start_time = time.time()
        response = llm.process_message(message)
        elapsed = time.time() - start_time

        logging.info(f"LLM Response: {response} (in {elapsed:.2f}s)")

        reply = {
            "drone_id": drone_id,
            "response": response,
            "latency_sec": round(elapsed, 2)
        }

        client.publish(output_topic, json.dumps(reply))
        logging.info(f"Published response to {output_topic}")

        send_to_thingsboard(drone_id, response)

    except json.JSONDecodeError:
        logging.error("Failed to decode incoming message as JSON.")
    except Exception as e:
        logging.error(f"Unexpected error processing message: {e}", exc_info=True)

client = mqtt.Client()
client.on_message = on_message


try:
    client.connect(broker, port, keepalive=60)
    client.subscribe(input_topic)
    logging.info(f"Subscribed to topic: {input_topic}")
except Exception as e:
    logging.critical(f"Failed to connect or subscribe: {e}")
    exit(1)

try:
    client.loop_forever()
except KeyboardInterrupt:
    logging.info("Stopped by user.")
    client.disconnect()
