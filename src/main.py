import time

import paho.mqtt.client as mqtt

from src.config import BROKER_IP, BROKER_PORT, JAR_SENSOR_TOPIC, DEFECT_TOPIC
from src.logger import setup_logging
from src.utils import bool_to_bytes, bytes_to_bool
from src.inference import run_inference

logger = setup_logging("mqtt_service")


def on_connect(client: mqtt.Client, userdata, flags, reason_code, properties) -> None:
    logger.info(f"Connected with result code {reason_code}")
    logger.info(f"Subscribing to {JAR_SENSOR_TOPIC}")
    result = client.subscribe(JAR_SENSOR_TOPIC)
    logger.info(f"Subscription result: {result}")


def on_message(client: mqtt.Client, userdata, msg) -> None:
    start = time.time()
    logger.debug(f"Received message on topic {msg.topic}: {msg.payload}")
    if msg.topic == JAR_SENSOR_TOPIC and bytes_to_bool(msg.payload):
        result = run_inference()
        logger.debug(f"Time from msg recv to inference complete: {time.time() - start}s")
        client.publish(DEFECT_TOPIC, bool_to_bytes(result))
        logger.debug(f"Time from msg recv to publ: {time.time() - start}s")
        logger.debug(f"Published result {result} to topic {DEFECT_TOPIC}")


def main():
    logger.info("Starting MQTT service")
    mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    mqttc.on_connect = on_connect
    mqttc.on_message = on_message

    try:
        logger.info(f"Connecting to broker {BROKER_IP}:{BROKER_PORT}")
        mqttc.connect(BROKER_IP, BROKER_PORT, 60)
    except Exception as e:
        logger.error(f"Failed to connect to broker: {e}")
        return

    time.sleep(3) # Give usb camera some time to wake up

    logger.info("Starting MQTT loop")
    mqttc.loop_forever()


if __name__ == "__main__":
    main()
