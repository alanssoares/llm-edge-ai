"""
Unit tests for IoT Device Simulator
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import pandas as pd
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / 'src'
sys.path.insert(0, str(src_path))

from device_simulator import IoTDeviceSimulator


class TestIoTDeviceSimulator:
    """Test cases for IoTDeviceSimulator class"""
    
    def test_device_initialization(self):
        """Test device initialization with basic parameters"""
        device = IoTDeviceSimulator(
            device_id="00:0f:00:70:91:0a",
            device_name="test-device"
        )
        
        assert device.device_id == "00:0f:00:70:91:0a"
        assert device.device_name == "test-device"
        assert device.mqtt_broker == "mqtt-broker"
        assert device.mqtt_port == 1883
        assert device.topic == "iot/telemetry/00:0f:00:70:91:0a"
        assert device.is_running is False
    
    def test_device_initialization_custom_broker(self):
        """Test device initialization with custom MQTT broker"""
        device = IoTDeviceSimulator(
            device_id="test-id",
            device_name="test-device",
            mqtt_broker="custom-broker",
            mqtt_port=8883
        )
        
        assert device.mqtt_broker == "custom-broker"
        assert device.mqtt_port == 8883
    
    def test_create_telemetry_message(self):
        """Test telemetry message creation"""
        device = IoTDeviceSimulator(
            device_id="00:0f:00:70:91:0a",
            device_name="test-device"
        )
        
        # Create a mock pandas Series
        row = pd.Series({
            'ts': 1594512000.0,
            'co': 0.0045,
            'humidity': 51.0,
            'light': False,
            'lpg': 0.0076,
            'motion': False,
            'smoke': 0.0234,
            'temp': 86.0
        })
        
        message = device.create_telemetry_message(row)
        
        assert message['device_id'] == "00:0f:00:70:91:0a"
        assert message['ts'] == 1594512000.0
        assert message['data']['temp'] == 86.0
        assert message['data']['humidity'] == 51.0
        assert message['data']['co'] == 0.0045
        assert message['data']['light'] is False
        assert message['data']['motion'] is False
    
    @patch('device_simulator.pd.read_csv')
    def test_load_dataset_success(self, mock_read_csv):
        """Test successful dataset loading"""
        # Mock DataFrame
        mock_df = pd.DataFrame({
            'device': ['00:0f:00:70:91:0a', '00:0f:00:70:91:0a'],
            'ts': [1594512000.0, 1594512060.0],
            'co': [0.0045, 0.0046],
            'humidity': [51.0, 52.0],
            'light': [False, False],
            'lpg': [0.0076, 0.0077],
            'motion': [False, True],
            'smoke': [0.0234, 0.0235],
            'temp': [86.0, 86.5]
        })
        mock_read_csv.return_value = mock_df
        
        device = IoTDeviceSimulator(
            device_id="00:0f:00:70:91:0a",
            device_name="test-device"
        )
        
        device.load_dataset("/fake/path/data.csv")
        
        assert device.data is not None
        assert len(device.data) == 2
        assert device.device_id == "00:0f:00:70:91:0a"
    
    @patch('device_simulator.pd.read_csv')
    def test_load_dataset_device_not_found(self, mock_read_csv):
        """Test dataset loading when device ID not found"""
        # Mock DataFrame with different device ID
        mock_df = pd.DataFrame({
            'device': ['different-device-id'],
            'ts': [1594512000.0],
            'co': [0.0045],
            'humidity': [51.0],
            'light': [False],
            'lpg': [0.0076],
            'motion': [False],
            'smoke': [0.0234],
            'temp': [86.0]
        })
        mock_read_csv.return_value = mock_df
        
        device = IoTDeviceSimulator(
            device_id="00:0f:00:70:91:0a",
            device_name="test-device"
        )
        
        device.load_dataset("/fake/path/data.csv")
        
        # Should fall back to first available device
        assert device.data is not None
        assert len(device.data) == 1
        assert device.device_id == "different-device-id"
    
    def test_on_connect_success(self):
        """Test successful MQTT connection callback"""
        device = IoTDeviceSimulator(
            device_id="test-id",
            device_name="test-device"
        )
        
        mock_client = Mock()
        device.on_connect(mock_client, None, None, 0)
        
        assert device.is_running is True
    
    def test_on_connect_failure(self):
        """Test failed MQTT connection callback"""
        device = IoTDeviceSimulator(
            device_id="test-id",
            device_name="test-device"
        )
        
        mock_client = Mock()
        device.on_connect(mock_client, None, None, 1)
        
        assert device.is_running is False
    
    def test_on_disconnect(self):
        """Test MQTT disconnect callback"""
        device = IoTDeviceSimulator(
            device_id="test-id",
            device_name="test-device"
        )
        device.is_running = True
        
        mock_client = Mock()
        device.on_disconnect(mock_client, None, 0)
        
        assert device.is_running is False


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
