import time

import paho.mqtt.client as mqtt

from src.config import BROKER_IP, BROKER_PORT, JAR_SENSOR_TOPIC

mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqttc.connect(BROKER_IP, BROKER_PORT, 60)

# Non-blocking call that processes network traffic, dispatches callbacks and handles reconnecting.
mqttc.loop_start()

while True:
    mqttc.publish(JAR_SENSOR_TOPIC, b"1")
    time.sleep(1)

mqttc.loop_stop()
