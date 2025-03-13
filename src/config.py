import os
from dotenv import load_dotenv

load_dotenv()

BROKER_IP = os.getenv("BROKER_IP")
BROKER_PORT = int(os.getenv("BROKER_PORT"))
JAR_SENSOR_TOPIC = os.getenv("JAR_SENSOR_TOPIC")
DEFECT_TOPIC = os.getenv("DEFECT_TOPIC")
