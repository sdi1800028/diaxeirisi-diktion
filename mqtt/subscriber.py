import paho.mqtt.client as mqtt
import json
import logging
from llm_model import DroneLLM

logging.basicConfig(level=logging.INFO)

llm = DroneLLM()
broker = "localhost"
port = 1883
obstacle_topic = "drone/obstacles"
navigation_topic_template = "drone/{drone_id}/navigation"

def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())
        logging.info(f"Received obstacle data: {data}")

        drone_id = data.get("drone_id", "unknown")
        llm_response = llm.process_message(data)
        logging.info(f"LLM Decision: {llm_response}")

        nav_msg = {
            "drone_id": drone_id,
            "response": llm_response,
            "timestamp": time.time()
        }
        nav_topic = navigation_topic_template.format(drone_id=drone_id)
        client.publish(nav_topic, json.dumps(nav_msg), qos=1)
        logging.info(f"Published LLM response to {nav_topic}: {nav_msg}")

    except json.JSONDecodeError:
        logging.error("Malformed JSON payload.")
    except Exception as e:
        logging.exception(f"Unexpected error: {e}")

client = mqtt.Client()
client.on_message = on_message

try:
    client.connect(broker, port, 60)
    client.subscribe(obstacle_topic, qos=1)
    logging.info(f"Subscribed to topic: {obstacle_topic}")
    client.loop_forever()

except Exception as e:
    logging.exception("Subscriber failed to connect or run.")
