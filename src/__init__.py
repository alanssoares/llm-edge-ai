"""
IoT Edge AI - Device Simulator Package
Simulates IoT edge devices with MQTT telemetry
"""

__version__ = "0.1.0"
__author__ = "UFBA - LLM Edge AI Team"

from .device_simulator import IoTDeviceSimulator
from .mqtt_consumer import MQTTTelemetryConsumer
from .generate_compose import generate_compose, get_device_id_from_dataset

__all__ = [
    'IoTDeviceSimulator',
    'MQTTTelemetryConsumer',
    'generate_compose',
    'get_device_id_from_dataset',
]
