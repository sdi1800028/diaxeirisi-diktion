import paho.mqtt.client as mqtt
import json
import logging

# Logging
logging.basicConfig(level=logging.INFO)

broker = "localhost"
port = 1883
topic = "drone/obstacles"

obstacle_data = {
    "type": "obstacle",
    "object": "tree",
    "position": {"x": 25, "y": 30},
    "height": 15,
    "movement": "stationary"
}

try:
    client = mqtt.Client()
    client.connect(broker, port, 60)
    payload = json.dumps(obstacle_data)
    result = client.publish(topic, payload, qos=1)

    if result.rc == mqtt.MQTT_ERR_SUCCESS:
        logging.info(f"Published successfully: {payload}")
    else:
        logging.error("Failed to publish message.")
    
    client.disconnect()

except Exception as e:
    logging.exception(f"MQTT Publisher error: {e}")
