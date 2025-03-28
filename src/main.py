import time

import paho.mqtt.client as mqtt

from src.config import BROKER_IP, BROKER_PORT, CONNECT_TIMEOUT, DEFECT_TOPIC, JAR_SENSOR_TOPIC
from src.inference import run_inference
from src.logger import setup_logging
from src.utils import bool_to_bytes, bytes_to_bool

logger = setup_logging("mqtt_service")


def on_connect(client: mqtt.Client, userdata, flags, reason_code, properties) -> None:
    logger.info(f"Connected with result code {reason_code}")
    logger.info(f"Subscribing to {JAR_SENSOR_TOPIC}")
    result = client.subscribe(JAR_SENSOR_TOPIC)
    logger.info(f"Subscription result: {result}")


def on_connect_fail(client: mqtt.Client, userdata):
    logger.error("Failed to connect to mqtt broker. Exiting.")
    exit()


def on_disconnect(client: mqtt.Client, userdata, disconnect_flags, reason_code, properties):
    logger.info(f"Disconnected with reason code {reason_code}")
    logger.info(f"Connecting to broker {BROKER_IP}:{BROKER_PORT}")
    client.connect(BROKER_IP, BROKER_PORT, 60)


def on_message(client: mqtt.Client, userdata, msg) -> None:
    start = time.time()
    logger.debug(f"Received message on topic {msg.topic}: {msg.payload}")
    try:
        jar_present = bytes_to_bool(msg.payload)
    except ValueError as e:
        logger.error(
            f"Received message from sensor that could not be converted to bool: {e}. Skipping inference"
        )
        jar_present = False
    if msg.topic == JAR_SENSOR_TOPIC and jar_present:
        result = run_inference()
        logger.debug(f"Time from msg recv to inference complete: {(time.time() - start) * 1000} ms")
        client.publish(DEFECT_TOPIC, bool_to_bytes(result))
        logger.debug(f"Time from msg recv to publ: {(time.time() - start) * 1000} ms")
        logger.debug(f"Published result {result} to topic {DEFECT_TOPIC}")


def main():
    logger.info("Starting MQTT service")
    mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    mqttc.connect_timeout = CONNECT_TIMEOUT
    mqttc.on_connect = on_connect
    mqttc.on_message = on_message
    mqttc.on_disconnect = on_disconnect
    mqttc.on_connect_fail = on_connect_fail

    try:
        logger.info(f"Connecting to broker {BROKER_IP}:{BROKER_PORT}")
        mqttc.connect(BROKER_IP, BROKER_PORT, 60)
    except Exception as e:
        logger.error(f"Failed to connect to broker: {e}")
        return

    logger.info("Starting MQTT loop")
    mqttc.loop_forever()


if __name__ == "__main__":
    main()
