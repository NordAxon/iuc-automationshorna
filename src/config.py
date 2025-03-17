import os
from dotenv import load_dotenv

load_dotenv()


def get_env_var(name: str, convert_type=None):
    """Get environment variable or raise error if not set."""
    value = os.getenv(name)
    if value is None:
        raise ValueError(f"Environment variable {name} is not set")
    if convert_type:
        try:
            return convert_type(value)
        except ValueError:
            raise ValueError(
                f"Environment variable {name} could not be converted to {convert_type.__name__}"
            )
    return value


# MQTT Configuration
BROKER_IP = get_env_var("BROKER_IP")
BROKER_PORT = get_env_var("BROKER_PORT", int)
JAR_SENSOR_TOPIC = get_env_var("JAR_SENSOR_TOPIC")
DEFECT_TOPIC = get_env_var("DEFECT_TOPIC")
CONNECT_TIMEOUT = get_env_var("CONNECT_TIMEOUT", int)

# Inference Configuration
MODEL_PATH = get_env_var("MODEL_PATH")
INFERENCE_DEVICE = get_env_var("INFERENCE_DEVICE")
IMAGE_HEIGHT = get_env_var("IMAGE_HEIGHT", int)
IMAGE_WIDTH = get_env_var("IMAGE_WIDTH", int)
IMAGE_SOURCE = get_env_var("IMAGE_SOURCE")
IMAGE_ROTATION = get_env_var("IMAGE_ROTATION", int)
GET_IMAGE_TIMEOUT = get_env_var("GET_IMAGE_TIMEOUT", float)

# Logging Configuration
LOG_LEVEL = get_env_var("LOG_LEVEL")
