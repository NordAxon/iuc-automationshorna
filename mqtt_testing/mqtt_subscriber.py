import paho.mqtt.client as mqtt

from src.config import BROKER_IP, BROKER_PORT, DEFECT_TOPIC


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client: mqtt.Client, userdata, flags, reason_code, properties):
    print(f"Connected with result code {reason_code}")
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    result = client.subscribe(DEFECT_TOPIC)
    print(result)


# The callback for when a PUBLISH message is received from the server.
def on_message(client: mqtt.Client, userdata, msg):
    print(msg.topic + " " + str(msg.payload))


mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqttc.on_connect = on_connect
mqttc.on_message = on_message

mqttc.connect(BROKER_IP, BROKER_PORT, 60)

# Blocking call that processes network traffic, dispatches callbacks and handles reconnecting.
mqttc.loop_forever()
