#!/usr/bin/env python3
"""
IoT Device Simulator
Simulates IoT devices sending telemetry data via MQTT based on real dataset
"""

import json
import time
import random
import pandas as pd
import paho.mqtt.client as mqtt
import os
import sys
from datetime import datetime
from typing import Dict, Any

class IoTDeviceSimulator:
    def __init__(self, device_id: str, device_name: str, mqtt_broker: str = "mqtt-broker", mqtt_port: int = 1883):
        self.device_id = device_id
        self.device_name = device_name
        self.mqtt_broker = mqtt_broker
        self.mqtt_port = mqtt_port
        self.client = None
        self.data = None
        self.current_index = 0
        self.is_running = False
        
        # MQTT topic for this device
        self.topic = f"iot/telemetry/{device_id}"
        
        print(f"Initializing device: {device_name} (ID: {device_id})")
        print(f"MQTT Broker: {mqtt_broker}:{mqtt_port}")
        print(f"Topic: {self.topic}")
    
    def load_dataset(self, csv_path: str = "/app/dataset/iot_telemetry_data.csv"):
        """Load the telemetry dataset and filter for this device"""
        try:
            print(f"Loading dataset from: {csv_path}")
            df = pd.read_csv(csv_path)
            
            # Filter data for this specific device
            device_data = df[df['device'] == self.device_id]
            
            if device_data.empty:
                print(f"Warning: No data found for device {self.device_id}")
                print(f"Available devices: {df['device'].unique()}")
                # Use first available device if this one doesn't exist
                if not df.empty:
                    self.device_id = df['device'].iloc[0]
                    device_data = df[df['device'] == self.device_id]
                    print(f"Using device: {self.device_id}")
            
            self.data = device_data.reset_index(drop=True)
            print(f"Loaded {len(self.data)} records for device {self.device_id}")
            
        except Exception as e:
            print(f"Error loading dataset: {e}")
            sys.exit(1)
    
    def on_connect(self, client, userdata, flags, rc):
        """Callback for when the client connects to the broker"""
        if rc == 0:
            print(f"Connected to MQTT broker successfully")
            self.is_running = True
        else:
            print(f"Failed to connect to MQTT broker. Return code: {rc}")
            self.is_running = False
    
    def on_disconnect(self, client, userdata, rc):
        """Callback for when the client disconnects from the broker"""
        print(f"Disconnected from MQTT broker. Return code: {rc}")
        self.is_running = False
    
    def on_publish(self, client, userdata, mid):
        """Callback for when a message is published"""
        print(f"Message published successfully (mid: {mid})")
    
    def connect_mqtt(self):
        """Connect to MQTT broker"""
        try:
            self.client = mqtt.Client(client_id=f"{self.device_name}_{self.device_id}")
            self.client.on_connect = self.on_connect
            self.client.on_disconnect = self.on_disconnect
            self.client.on_publish = self.on_publish
            
            print(f"Connecting to MQTT broker at {self.mqtt_broker}:{self.mqtt_port}")
            self.client.connect(self.mqtt_broker, self.mqtt_port, 60)
            self.client.loop_start()
            
            # Wait for connection
            timeout = 10
            while not self.is_running and timeout > 0:
                time.sleep(1)
                timeout -= 1
            
            if not self.is_running:
                raise Exception("Failed to connect to MQTT broker within timeout")
                
        except Exception as e:
            print(f"Error connecting to MQTT broker: {e}")
            sys.exit(1)
    
    def create_telemetry_message(self, row: pd.Series) -> Dict[str, Any]:
        """Create a telemetry message in the same format as the original dataset"""
        # Convert timestamp to epoch if it's in scientific notation
        timestamp = row['ts']
        if isinstance(timestamp, str) and 'E' in timestamp:
            timestamp = float(timestamp)
        
        message = {
            "data": {
                "co": float(row['co']),
                "humidity": float(row['humidity']),
                "light": bool(row['light']),
                "lpg": float(row['lpg']),
                "motion": bool(row['motion']),
                "smoke": float(row['smoke']),
                "temp": float(row['temp'])
            },
            "device_id": self.device_id,
            "ts": timestamp
        }
        return message
    
    def send_telemetry(self):
        """Send telemetry data in a loop"""
        if self.data is None or self.data.empty:
            print("No data available to send")
            return
        
        print(f"Starting to send telemetry data for device {self.device_id}")
        print(f"Will send {len(self.data)} messages, cycling through the dataset")
        
        while self.is_running:
            try:
                # Get current row
                row = self.data.iloc[self.current_index]
                
                # Create message
                message = self.create_telemetry_message(row)
                
                # Publish message
                payload = json.dumps(message, indent=None)
                result = self.client.publish(self.topic, payload, qos=1)
                
                if result.rc == mqtt.MQTT_ERR_SUCCESS:
                    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Sent telemetry: "
                          f"temp={message['data']['temp']:.1f}°F, "
                          f"humidity={message['data']['humidity']:.1f}%, "
                          f"co={message['data']['co']:.4f}ppm")
                else:
                    print(f"Failed to publish message: {result.rc}")
                
                # Move to next record
                self.current_index = (self.current_index + 1) % len(self.data)
                
                # Wait before sending next message (simulate real device behavior)
                # Random interval between 1-5 seconds
                sleep_time = random.uniform(1, 5)
                time.sleep(sleep_time)
                
            except KeyboardInterrupt:
                print("Received interrupt signal, stopping...")
                break
            except Exception as e:
                print(f"Error sending telemetry: {e}")
                time.sleep(5)  # Wait before retrying
    
    def run(self):
        """Main run method"""
        print(f"Starting IoT Device Simulator for {self.device_name}")
        
        # Load dataset
        self.load_dataset()
        
        # Connect to MQTT broker
        self.connect_mqtt()
        
        # Start sending telemetry
        try:
            self.send_telemetry()
        except KeyboardInterrupt:
            print("Shutting down...")
        finally:
            if self.client:
                self.client.loop_stop()
                self.client.disconnect()
            print("Device simulator stopped")

def main():
    """Main entry point"""
    # Get configuration from environment variables
    device_name = os.getenv('DEVICE_NAME', 'edge-device')
    device_id = os.getenv('DEVICE_ID', '00:0f:00:70:91:0a')
    mqtt_broker = os.getenv('MQTT_BROKER', 'mqtt-broker')
    mqtt_port = int(os.getenv('MQTT_PORT', '1883'))
    
    # Create and run simulator
    simulator = IoTDeviceSimulator(
        device_id=device_id,
        device_name=device_name,
        mqtt_broker=mqtt_broker,
        mqtt_port=mqtt_port
    )
    
    simulator.run()

if __name__ == "__main__":
    main()
