#!/usr/bin/env python3
"""
IoT Device Simulator
Simulates IoT devices sending telemetry data via MQTT based on real dataset
Now includes LLM inference capabilities for edge AI processing
"""

import json
import time
import random
import pandas as pd
import paho.mqtt.client as mqtt
import os
import sys
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Import LLM inference engine
try:
    from llm_inference import LLMInferenceEngine
    LLM_AVAILABLE = True
except ImportError as e:
    logger_temp = logging.getLogger(__name__)
    logger_temp.warning(f"LLM inference not available: {e}")
    LLM_AVAILABLE = False

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=os.getenv('LOG_LEVEL', 'INFO'),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


class IoTDeviceSimulator:
    """Simulates an IoT device sending telemetry data via MQTT with LLM inference"""
    
    def __init__(
        self,
        device_id: str,
        device_name: str,
        mqtt_broker: str = "mqtt-broker",
        mqtt_port: int = 1883,
        enable_llm: bool = False
    ):
        """
        Initialize the IoT device simulator
        
        Args:
            device_id: Unique device identifier (MAC address format)
            device_name: Human-readable device name
            mqtt_broker: MQTT broker hostname or IP
            mqtt_port: MQTT broker port (default: 1883)
            enable_llm: Whether to enable LLM inference on this device
        """
        self.device_id = device_id
        self.device_name = device_name
        self.mqtt_broker = mqtt_broker
        self.mqtt_port = mqtt_port
        self.client: Optional[mqtt.Client] = None
        self.data: Optional[pd.DataFrame] = None
        self.current_index = 0
        self.is_running = False
        
        # LLM inference engine
        self.enable_llm = enable_llm and LLM_AVAILABLE
        self.llm_engine: Optional[LLMInferenceEngine] = None
        self.llm_inference_interval = int(os.getenv('LLM_INFERENCE_INTERVAL', '5'))  # Run LLM every N messages
        self.message_count = 0
        
        # MQTT topics
        self.topic = f"iot/telemetry/{device_id}"
        self.analysis_topic = f"iot/analysis/{device_id}"
        self.metrics_topic = f"iot/metrics/{device_id}"
        
        logger.info(f"Initializing device: {device_name} (ID: {device_id})")
        logger.info(f"MQTT Broker: {mqtt_broker}:{mqtt_port}")
        logger.info(f"Topic: {self.topic}")
        logger.info(f"LLM Inference: {'Enabled' if self.enable_llm else 'Disabled'}")
    
    def load_dataset(self, csv_path: str = "/app/dataset/iot_telemetry_data.csv") -> None:
        """
        Load the telemetry dataset and filter for this device
        
        Args:
            csv_path: Path to the CSV dataset file
        """
        try:
            logger.info(f"Loading dataset from: {csv_path}")
            df = pd.read_csv(csv_path)
            
            # Filter data for this specific device
            device_data = df[df['device'] == self.device_id]
            
            if device_data.empty:
                logger.warning(f"No data found for device {self.device_id}")
                logger.info(f"Available devices: {df['device'].unique()}")
                # Use first available device if this one doesn't exist
                if not df.empty:
                    self.device_id = df['device'].iloc[0]
                    device_data = df[df['device'] == self.device_id]
                    logger.info(f"Using device: {self.device_id}")
            
            self.data = device_data.reset_index(drop=True)
            logger.info(f"Loaded {len(self.data)} records for device {self.device_id}")
            
        except Exception as e:
            logger.error(f"Error loading dataset: {e}", exc_info=True)
            sys.exit(1)
    
    def on_connect(self, client: mqtt.Client, userdata: Any, flags: Dict, rc: int) -> None:
        """Callback for when the client connects to the broker"""
        if rc == 0:
            logger.info("Connected to MQTT broker successfully")
            self.is_running = True
        else:
            logger.error(f"Failed to connect to MQTT broker. Return code: {rc}")
            self.is_running = False
    
    def on_disconnect(self, client: mqtt.Client, userdata: Any, rc: int) -> None:
        """Callback for when the client disconnects from the broker"""
        logger.warning(f"Disconnected from MQTT broker. Return code: {rc}")
        self.is_running = False
    
    def on_publish(self, client: mqtt.Client, userdata: Any, mid: int) -> None:
        """Callback for when a message is published"""
        logger.debug(f"Message published successfully (mid: {mid})")
    
    def initialize_llm(self) -> None:
        """Initialize LLM inference engine if enabled"""
        if not self.enable_llm:
            logger.info("LLM inference is disabled")
            return
        
        try:
            logger.info("Initializing LLM inference engine...")
            model_name = os.getenv('LLM_MODEL_NAME', 'microsoft/Phi-3.5-mini-instruct')
            
            self.llm_engine = LLMInferenceEngine(
                model_name=model_name,
                device_id=self.device_id,
                max_length=int(os.getenv('LLM_MAX_LENGTH', '512')),
                temperature=float(os.getenv('LLM_TEMPERATURE', '0.7'))
            )
            
            logger.info("Loading LLM model (this may take a few minutes)...")
            self.llm_engine.load_model()
            logger.info("LLM model loaded successfully!")
            
        except Exception as e:
            logger.error(f"Error initializing LLM: {e}", exc_info=True)
            logger.warning("Continuing without LLM inference")
            self.enable_llm = False
            self.llm_engine = None
    
    def connect_mqtt(self) -> None:
        """Connect to MQTT broker"""
        try:
            self.client = mqtt.Client(client_id=f"{self.device_name}_{self.device_id}")
            self.client.on_connect = self.on_connect
            self.client.on_disconnect = self.on_disconnect
            self.client.on_publish = self.on_publish
            
            logger.info(f"Connecting to MQTT broker at {self.mqtt_broker}:{self.mqtt_port}")
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
            logger.error(f"Error connecting to MQTT broker: {e}", exc_info=True)
            sys.exit(1)
    
    def create_telemetry_message(self, row: pd.Series) -> Dict[str, Any]:
        """
        Create a telemetry message in the same format as the original dataset
        
        Args:
            row: Pandas Series containing sensor data
            
        Returns:
            Dictionary with telemetry data
        """
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
    
    def process_telemetry_with_llm(self, message: Dict[str, Any]) -> None:
        """
        Process telemetry data with LLM inference
        
        Args:
            message: Telemetry message dictionary
        """
        if not self.enable_llm or self.llm_engine is None:
            return
        
        try:
            logger.info("Running LLM inference on telemetry data...")
            
            # Perform inference and collect metrics
            result = self.llm_engine.analyze_telemetry(message)
            
            # Publish analysis result
            analysis_payload = json.dumps({
                'device_id': self.device_id,
                'timestamp': datetime.now().isoformat(),
                'analysis': result['analysis'],
                'telemetry': result['telemetry_input']
            })
            self.client.publish(self.analysis_topic, analysis_payload, qos=1)
            logger.info("Published LLM analysis result")
            
            # Publish metrics
            metrics_payload = json.dumps(result['metrics'])
            self.client.publish(self.metrics_topic, metrics_payload, qos=1)
            logger.debug("Published inference metrics")
            
        except Exception as e:
            logger.error(f"Error processing telemetry with LLM: {e}", exc_info=True)
    
    def send_telemetry(self) -> None:
        """Send telemetry data in a loop with optional LLM inference"""
        if self.data is None or self.data.empty:
            logger.error("No data available to send")
            return
        
        logger.info(f"Starting to send telemetry data for device {self.device_id}")
        logger.info(f"Will send {len(self.data)} messages, cycling through the dataset")
        
        if self.enable_llm:
            logger.info(f"LLM inference will run every {self.llm_inference_interval} messages")
        
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
                    self.message_count += 1
                    logger.info(
                        f"Sent telemetry #{self.message_count}: "
                        f"temp={message['data']['temp']:.1f}°F, "
                        f"humidity={message['data']['humidity']:.1f}%, "
                        f"co={message['data']['co']:.4f}ppm"
                    )
                    
                    # Run LLM inference at specified intervals
                    if self.enable_llm and self.message_count % self.llm_inference_interval == 0:
                        self.process_telemetry_with_llm(message)
                        
                        # Save metrics periodically
                        if self.message_count % (self.llm_inference_interval * 10) == 0:
                            self.save_metrics()
                else:
                    logger.error(f"Failed to publish message: {result.rc}")
                
                # Move to next record
                self.current_index = (self.current_index + 1) % len(self.data)
                
                # Wait before sending next message (simulate real device behavior)
                # Random interval between 1-5 seconds
                sleep_time = random.uniform(1, 5)
                time.sleep(sleep_time)
                
            except KeyboardInterrupt:
                logger.info("Received interrupt signal, stopping...")
                break
            except Exception as e:
                logger.error(f"Error sending telemetry: {e}", exc_info=True)
                time.sleep(5)  # Wait before retrying
    
    def save_metrics(self) -> None:
        """Save LLM inference metrics"""
        if self.llm_engine is None:
            return
        
        try:
            logger.info("Saving inference metrics...")
            filepath = self.llm_engine.save_metrics()
            logger.info(f"Metrics saved to: {filepath}")
            
            # Also publish summary to MQTT
            summary = self.llm_engine.get_metrics_summary()
            summary_payload = json.dumps(summary)
            self.client.publish(f"{self.metrics_topic}/summary", summary_payload, qos=1)
            
        except Exception as e:
            logger.error(f"Error saving metrics: {e}", exc_info=True)
    
    def run(self) -> None:
        """Main run method"""
        logger.info(f"Starting IoT Device Simulator for {self.device_name}")
        
        # Load dataset
        self.load_dataset()
        
        # Initialize LLM if enabled
        self.initialize_llm()
        
        # Connect to MQTT broker
        self.connect_mqtt()
        
        # Start sending telemetry
        try:
            self.send_telemetry()
        except KeyboardInterrupt:
            logger.info("Shutting down...")
        finally:
            # Save final metrics
            if self.enable_llm:
                self.save_metrics()
            
            if self.client:
                self.client.loop_stop()
                self.client.disconnect()
            logger.info("Device simulator stopped")


def main():
    """Main entry point"""
    # Get configuration from environment variables
    device_name = os.getenv('DEVICE_NAME', 'edge-device')
    device_id = os.getenv('DEVICE_ID', '00:0f:00:70:91:0a')
    mqtt_broker = os.getenv('MQTT_BROKER', 'mqtt-broker')
    mqtt_port = int(os.getenv('MQTT_PORT', '1883'))
    
    # LLM configuration
    enable_llm = os.getenv('ENABLE_LLM', 'false').lower() in ('true', '1', 'yes')
    
    logger.info("="*60)
    logger.info(f"Device Configuration:")
    logger.info(f"  Name: {device_name}")
    logger.info(f"  ID: {device_id}")
    logger.info(f"  MQTT Broker: {mqtt_broker}:{mqtt_port}")
    logger.info(f"  LLM Inference: {enable_llm}")
    if enable_llm:
        logger.info(f"  LLM Model: {os.getenv('LLM_MODEL_NAME', 'microsoft/Phi-3.5-mini-instruct')}")
    logger.info("="*60)
    
    # Create and run simulator
    simulator = IoTDeviceSimulator(
        device_id=device_id,
        device_name=device_name,
        mqtt_broker=mqtt_broker,
        mqtt_port=mqtt_port,
        enable_llm=enable_llm
    )
    
    simulator.run()


if __name__ == "__main__":
    main()
