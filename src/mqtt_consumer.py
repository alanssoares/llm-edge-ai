#!/usr/bin/env python3
"""
MQTT Consumer for IoT Telemetry Data
Consumes telemetry data from IoT devices via MQTT
"""

import json
import paho.mqtt.client as mqtt
import os
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=os.getenv('LOG_LEVEL', 'INFO'),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


class MQTTTelemetryConsumer:
    """Consumes and displays telemetry data from IoT devices via MQTT"""
    
    def __init__(self, mqtt_broker: str = "localhost", mqtt_port: int = 1883):
        """
        Initialize the MQTT telemetry consumer
        
        Args:
            mqtt_broker: MQTT broker hostname or IP
            mqtt_port: MQTT broker port (default: 1883)
        """
        self.mqtt_broker = mqtt_broker
        self.mqtt_port = mqtt_port
        self.client: Optional[mqtt.Client] = None
        self.is_connected = False
        
        logger.info("Initializing MQTT Consumer")
        logger.info(f"MQTT Broker: {mqtt_broker}:{mqtt_port}")
    
    def on_connect(self, client: mqtt.Client, userdata: Any, flags: Dict, rc: int) -> None:
        """Callback for when the client connects to the broker"""
        if rc == 0:
            logger.info("Connected to MQTT broker successfully")
            self.is_connected = True
            
            # Subscribe to all telemetry topics
            topic = "iot/telemetry/+"
            client.subscribe(topic)
            logger.info(f"Subscribed to topic: {topic}")
        else:
            logger.error(f"Failed to connect to MQTT broker. Return code: {rc}")
            self.is_connected = False
    
    def on_disconnect(self, client: mqtt.Client, userdata: Any, rc: int) -> None:
        """Callback for when the client disconnects from the broker"""
        logger.warning(f"Disconnected from MQTT broker. Return code: {rc}")
        self.is_connected = False
    
    def on_message(self, client: mqtt.Client, userdata: Any, msg: mqtt.MQTTMessage) -> None:
        """Callback for when a message is received"""
        try:
            # Parse the message
            payload = json.loads(msg.payload.decode())
            device_id = payload.get('device_id', 'unknown')
            timestamp = payload.get('ts', 0)
            data = payload.get('data', {})
            
            # Convert timestamp to readable format
            if timestamp:
                dt = datetime.fromtimestamp(timestamp)
                time_str = dt.strftime('%Y-%m-%d %H:%M:%S')
            else:
                time_str = "unknown"
            
            # Print telemetry data
            print(f"\n{'='*60}")
            print(f"Device: {device_id}")
            print(f"Timestamp: {time_str}")
            print(f"Topic: {msg.topic}")
            print(f"QoS: {msg.qos}")
            print(f"Data:")
            print(f"  Temperature: {data.get('temp', 'N/A'):.1f}°F")
            print(f"  Humidity: {data.get('humidity', 'N/A'):.1f}%")
            print(f"  CO: {data.get('co', 'N/A'):.4f} ppm")
            print(f"  LPG: {data.get('lpg', 'N/A'):.4f} ppm")
            print(f"  Smoke: {data.get('smoke', 'N/A'):.4f} ppm")
            print(f"  Light: {'ON' if data.get('light') else 'OFF'}")
            print(f"  Motion: {'DETECTED' if data.get('motion') else 'NONE'}")
            print(f"{'='*60}")
            
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON message: {e}")
            logger.debug(f"Raw message: {msg.payload.decode()}")
        except Exception as e:
            logger.error(f"Error processing message: {e}", exc_info=True)
    
    def on_subscribe(self, client: mqtt.Client, userdata: Any, mid: int, granted_qos: tuple) -> None:
        """Callback for when a subscription is successful"""
        logger.info(f"Successfully subscribed (mid: {mid}, QoS: {granted_qos})")
    
    def connect_and_listen(self) -> None:
        """Connect to MQTT broker and start listening for messages"""
        try:
            self.client = mqtt.Client(client_id="telemetry_consumer")
            self.client.on_connect = self.on_connect
            self.client.on_disconnect = self.on_disconnect
            self.client.on_message = self.on_message
            self.client.on_subscribe = self.on_subscribe
            
            logger.info(f"Connecting to MQTT broker at {self.mqtt_broker}:{self.mqtt_port}")
            self.client.connect(self.mqtt_broker, self.mqtt_port, 60)
            
            logger.info("Starting to listen for telemetry data...")
            logger.info("Press Ctrl+C to stop")
            
            # Start the loop
            self.client.loop_forever()
            
        except KeyboardInterrupt:
            logger.info("\nShutting down...")
        except Exception as e:
            logger.error(f"Error: {e}", exc_info=True)
        finally:
            if self.client:
                self.client.disconnect()
            logger.info("MQTT Consumer stopped")


def main():
    """Main entry point"""
    # Get configuration from environment variables or use defaults
    mqtt_broker = os.getenv('MQTT_BROKER', 'localhost')
    mqtt_port = int(os.getenv('MQTT_PORT', '1883'))
    
    # Create and run consumer
    consumer = MQTTTelemetryConsumer(
        mqtt_broker=mqtt_broker,
        mqtt_port=mqtt_port
    )
    
    consumer.connect_and_listen()


if __name__ == "__main__":
    main()
