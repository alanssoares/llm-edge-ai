#!/usr/bin/env python3
"""
MQTT Consumer for IoT Telemetry Data
Consumes telemetry data from IoT devices via MQTT
"""

import json
import paho.mqtt.client as mqtt
import os
from datetime import datetime
from typing import Dict, Any

class MQTTTelemetryConsumer:
    def __init__(self, mqtt_broker: str = "localhost", mqtt_port: int = 1883):
        self.mqtt_broker = mqtt_broker
        self.mqtt_port = mqtt_port
        self.client = None
        self.is_connected = False
        
        print(f"Initializing MQTT Consumer")
        print(f"MQTT Broker: {mqtt_broker}:{mqtt_port}")
    
    def on_connect(self, client, userdata, flags, rc):
        """Callback for when the client connects to the broker"""
        if rc == 0:
            print(f"Connected to MQTT broker successfully")
            self.is_connected = True
            
            # Subscribe to all telemetry topics
            topic = "iot/telemetry/+"
            client.subscribe(topic)
            print(f"Subscribed to topic: {topic}")
        else:
            print(f"Failed to connect to MQTT broker. Return code: {rc}")
            self.is_connected = False
    
    def on_disconnect(self, client, userdata, rc):
        """Callback for when the client disconnects from the broker"""
        print(f"Disconnected from MQTT broker. Return code: {rc}")
        self.is_connected = False
    
    def on_message(self, client, userdata, msg):
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
            print(f"Error parsing JSON message: {e}")
            print(f"Raw message: {msg.payload.decode()}")
        except Exception as e:
            print(f"Error processing message: {e}")
    
    def on_subscribe(self, client, userdata, mid, granted_qos):
        """Callback for when a subscription is successful"""
        print(f"Successfully subscribed (mid: {mid}, QoS: {granted_qos})")
    
    def connect_and_listen(self):
        """Connect to MQTT broker and start listening for messages"""
        try:
            self.client = mqtt.Client(client_id="telemetry_consumer")
            self.client.on_connect = self.on_connect
            self.client.on_disconnect = self.on_disconnect
            self.client.on_message = self.on_message
            self.client.on_subscribe = self.on_subscribe
            
            print(f"Connecting to MQTT broker at {self.mqtt_broker}:{self.mqtt_port}")
            self.client.connect(self.mqtt_broker, self.mqtt_port, 60)
            
            print("Starting to listen for telemetry data...")
            print("Press Ctrl+C to stop")
            
            # Start the loop
            self.client.loop_forever()
            
        except KeyboardInterrupt:
            print("\nShutting down...")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            if self.client:
                self.client.disconnect()
            print("MQTT Consumer stopped")

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
