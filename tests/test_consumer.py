"""
Unit tests for MQTT Consumer
"""

import pytest
from unittest.mock import Mock, patch
import json
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / 'src'
sys.path.insert(0, str(src_path))

from mqtt_consumer import MQTTTelemetryConsumer


class TestMQTTTelemetryConsumer:
    """Test cases for MQTTTelemetryConsumer class"""
    
    def test_consumer_initialization(self):
        """Test consumer initialization with default parameters"""
        consumer = MQTTTelemetryConsumer()
        
        assert consumer.mqtt_broker == "localhost"
        assert consumer.mqtt_port == 1883
        assert consumer.is_connected is False
    
    def test_consumer_initialization_custom_broker(self):
        """Test consumer initialization with custom broker"""
        consumer = MQTTTelemetryConsumer(
            mqtt_broker="custom-broker",
            mqtt_port=8883
        )
        
        assert consumer.mqtt_broker == "custom-broker"
        assert consumer.mqtt_port == 8883
    
    def test_on_connect_success(self):
        """Test successful connection callback"""
        consumer = MQTTTelemetryConsumer()
        mock_client = Mock()
        
        consumer.on_connect(mock_client, None, None, 0)
        
        assert consumer.is_connected is True
        mock_client.subscribe.assert_called_once_with("iot/telemetry/+")
    
    def test_on_connect_failure(self):
        """Test failed connection callback"""
        consumer = MQTTTelemetryConsumer()
        mock_client = Mock()
        
        consumer.on_connect(mock_client, None, None, 1)
        
        assert consumer.is_connected is False
        mock_client.subscribe.assert_not_called()
    
    def test_on_disconnect(self):
        """Test disconnect callback"""
        consumer = MQTTTelemetryConsumer()
        consumer.is_connected = True
        mock_client = Mock()
        
        consumer.on_disconnect(mock_client, None, 0)
        
        assert consumer.is_connected is False
    
    def test_on_message_valid_payload(self, capsys):
        """Test message handling with valid payload"""
        consumer = MQTTTelemetryConsumer()
        mock_client = Mock()
        
        # Create mock message
        mock_msg = Mock()
        mock_msg.topic = "iot/telemetry/00:0f:00:70:91:0a"
        mock_msg.qos = 1
        
        payload = {
            "device_id": "00:0f:00:70:91:0a",
            "ts": 1594512000.0,
            "data": {
                "temp": 86.0,
                "humidity": 51.0,
                "co": 0.0045,
                "lpg": 0.0076,
                "smoke": 0.0234,
                "light": False,
                "motion": False
            }
        }
        mock_msg.payload.decode.return_value = json.dumps(payload)
        
        consumer.on_message(mock_client, None, mock_msg)
        
        # Check if output contains expected data
        captured = capsys.readouterr()
        assert "00:0f:00:70:91:0a" in captured.out
        assert "86.0" in captured.out
        assert "51.0" in captured.out
    
    def test_on_message_invalid_json(self, capsys):
        """Test message handling with invalid JSON"""
        consumer = MQTTTelemetryConsumer()
        mock_client = Mock()
        
        mock_msg = Mock()
        mock_msg.topic = "iot/telemetry/device-01"
        mock_msg.payload.decode.return_value = "invalid json"
        
        # Should not raise exception
        consumer.on_message(mock_client, None, mock_msg)
    
    def test_on_subscribe(self):
        """Test subscribe callback"""
        consumer = MQTTTelemetryConsumer()
        mock_client = Mock()
        
        # Should not raise exception
        consumer.on_subscribe(mock_client, None, 1, (0,))


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
