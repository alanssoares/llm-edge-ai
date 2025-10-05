"""
Unit tests for compose file generation
"""

import pytest
import yaml
import tempfile
import os
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / 'src'
sys.path.insert(0, str(src_path))

from generate_compose import generate_compose, get_device_id_from_dataset


class TestGenerateCompose:
    """Test cases for docker-compose generation"""
    
    def test_get_device_id_from_dataset(self):
        """Test device ID cycling from dataset"""
        # Should cycle through the 3 real device IDs
        device_id_0 = get_device_id_from_dataset(0)
        device_id_1 = get_device_id_from_dataset(1)
        device_id_2 = get_device_id_from_dataset(2)
        device_id_3 = get_device_id_from_dataset(3)  # Should cycle back
        
        assert device_id_0 == "00:0f:00:70:91:0a"
        assert device_id_1 == "1c:bf:ce:15:ec:4d"
        assert device_id_2 == "b8:27:eb:bf:9d:51"
        assert device_id_3 == device_id_0  # Cycles back
    
    def test_generate_compose_basic(self):
        """Test basic compose file generation"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.yml') as f:
            output_file = f.name
        
        try:
            result = generate_compose(
                num_devices=2,
                mqtt_enabled=True,
                output_file=output_file
            )
            
            assert result == output_file
            assert os.path.exists(output_file)
            
            # Parse and validate the generated file
            with open(output_file, 'r') as f:
                # Skip comment lines
                lines = [line for line in f if not line.strip().startswith('#')]
                content = ''.join(lines)
                compose_config = yaml.safe_load(content)
            
            # Check structure
            assert 'services' in compose_config
            assert 'networks' in compose_config
            assert 'volumes' in compose_config
            
            # Check MQTT broker
            assert 'mqtt-broker' in compose_config['services']
            
            # Check devices
            assert 'edge-device-01' in compose_config['services']
            assert 'edge-device-02' in compose_config['services']
            
            # Check network
            assert 'edge-network' in compose_config['networks']
            
        finally:
            if os.path.exists(output_file):
                os.remove(output_file)
    
    def test_generate_compose_without_mqtt(self):
        """Test compose generation without MQTT"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.yml') as f:
            output_file = f.name
        
        try:
            result = generate_compose(
                num_devices=1,
                mqtt_enabled=False,
                output_file=output_file
            )
            
            assert os.path.exists(output_file)
            
            with open(output_file, 'r') as f:
                lines = [line for line in f if not line.strip().startswith('#')]
                content = ''.join(lines)
                compose_config = yaml.safe_load(content)
            
            # Should not have MQTT broker
            assert 'mqtt-broker' not in compose_config['services']
            
            # Should have device
            assert 'edge-device-01' in compose_config['services']
            
        finally:
            if os.path.exists(output_file):
                os.remove(output_file)
    
    def test_generate_compose_large_scale(self):
        """Test compose generation with many devices"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.yml') as f:
            output_file = f.name
        
        try:
            result = generate_compose(
                num_devices=150,
                mqtt_enabled=True,
                output_file=output_file
            )
            
            assert os.path.exists(output_file)
            
            with open(output_file, 'r') as f:
                lines = [line for line in f if not line.strip().startswith('#')]
                content = ''.join(lines)
                compose_config = yaml.safe_load(content)
            
            # Check device naming with 3 digits
            assert 'edge-device-001' in compose_config['services']
            assert 'edge-device-100' in compose_config['services']
            assert 'edge-device-150' in compose_config['services']
            
            # Should have 150 devices + mqtt-broker + iot-device-image = 152 services
            assert len(compose_config['services']) == 152
            
        finally:
            if os.path.exists(output_file):
                os.remove(output_file)
    
    def test_device_environment_variables(self):
        """Test that devices have correct environment variables"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.yml') as f:
            output_file = f.name
        
        try:
            generate_compose(
                num_devices=1,
                mqtt_enabled=True,
                output_file=output_file
            )
            
            with open(output_file, 'r') as f:
                lines = [line for line in f if not line.strip().startswith('#')]
                content = ''.join(lines)
                compose_config = yaml.safe_load(content)
            
            device = compose_config['services']['edge-device-01']
            env_vars = device['environment']
            
            # Check environment variables
            assert any('DEVICE_NAME=edge-device-01' in var for var in env_vars)
            assert any('DEVICE_ID=' in var for var in env_vars)
            assert any('MQTT_BROKER=' in var for var in env_vars)
            
        finally:
            if os.path.exists(output_file):
                os.remove(output_file)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
