#!/usr/bin/env python3
"""
Generate docker-compose.yml with configurable number of IoT edge devices with MQTT telemetry.

Usage:
    python3 generate_compose.py --devices 10
    python3 generate_compose.py --devices 1000
    python3 generate_compose.py --devices 5 --mqtt-enabled
"""

import argparse
import yaml
import logging
from pathlib import Path
from typing import List

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def get_device_id_from_dataset(device_index: int) -> str:
    """
    Get realistic device IDs from the actual dataset.
    
    Args:
        device_index: Index of the device (0-based)
        
    Returns:
        Device ID in MAC address format
    """
    # Real device IDs from the IoT telemetry dataset
    real_device_ids = [
        "00:0f:00:70:91:0a",  # stable conditions, cooler and more humid
        "1c:bf:ce:15:ec:4d",  # highly variable temperature and humidity  
        "b8:27:eb:bf:9d:51"   # stable conditions, warmer and dryer
    ]
    
    # Cycle through real device IDs for realistic simulation
    return real_device_ids[device_index % len(real_device_ids)]


def generate_compose(
    num_devices: int,
    mqtt_enabled: bool = True,
    output_file: str = "docker-compose.yml"
) -> str:
    """
    Generate docker-compose.yml with specified number of devices.
    
    Args:
        num_devices: Number of edge devices to create
        mqtt_enabled: Whether to enable MQTT telemetry
        output_file: Output filename for the compose file
        
    Returns:
        Path to the generated file
    """
    logger.info(f"Generating docker-compose configuration for {num_devices} devices")
    
    compose_config = {
        'services': {},
        'volumes': {},
        'networks': {
            'edge-network': {
                'driver': 'bridge',
                'ipam': {
                    'config': [
                        {'subnet': '172.20.0.0/16'}
                    ]
                }
            }
        }
    }
    
    # Add MQTT broker service if enabled
    if mqtt_enabled:
        logger.info("Adding MQTT broker service")
        compose_config['services']['mqtt-broker'] = {
            'image': 'eclipse-mosquitto:1.6',
            'container_name': 'mqtt-broker',
            'hostname': 'mqtt-broker',
            'ports': [
                '1883:1883',    # MQTT port
                '9001:9001'     # WebSocket port
            ],
            'volumes': [
                './config/mosquitto.conf:/mosquitto/config/mosquitto.conf:ro',
                'mosquitto_data:/mosquitto/data',
                'mosquitto_logs:/mosquitto/log'
            ],
            'networks': ['edge-network'],
            'restart': 'unless-stopped'
        }
        
        # Add MQTT volumes
        compose_config['volumes'] = {
            'mosquitto_data': {'driver': 'local'},
            'mosquitto_logs': {'driver': 'local'}
        }
        
        # Add shared device image builder service with build optimizations
        compose_config['services']['iot-device-image'] = {
            'build': {
                'context': '.',
                'dockerfile': 'Dockerfile',
                'args': {
                    'BUILDKIT_INLINE_CACHE': '1'
                }
            },
            'image': 'iot-device-simulator:latest',
            'command': ['echo', 'This service builds the shared image for edge device simulation']
        }
    
    # Generate service for each device
    logger.info(f"Generating {num_devices} device configurations")
    for i in range(1, num_devices + 1):
        device_num = f"{i:02d}" if num_devices < 100 else f"{i:03d}" if num_devices < 1000 else f"{i:04d}"
        device_name = f"edge-device-{device_num}"
        
        if mqtt_enabled:
            # Use shared image with realistic device IDs for MQTT simulation
            device_id = get_device_id_from_dataset(i - 1)
            service_config = {
                'image': 'iot-device-simulator:latest',
                'container_name': device_name,
                'hostname': device_name,
                'environment': [
                    f'DEVICE_NAME={device_name}',
                    f'DEVICE_ID={device_id}',
                    'MQTT_BROKER=mqtt-broker',
                    'MQTT_PORT=1883'
                ],
                'volumes': [
                    './config:/etc/edge-device:ro',
                    './dataset:/app/dataset:ro'
                ],
                'networks': ['edge-network'],
                'depends_on': ['mqtt-broker', 'iot-device-image'],
                'restart': 'unless-stopped'
            }
        else:
            # Original configuration without MQTT
            service_config = {
                'build': {
                    'context': '.',
                    'dockerfile': 'Dockerfile'
                },
                'container_name': device_name,
                'hostname': device_name,
                'environment': [
                    f'DEVICE_NAME={device_name}',
                    f'DEVICE_ID={device_num}'
                ],
                'volumes': [
                    './config:/etc/edge-device:ro',
                    './dataset:/app/dataset:ro'
                ],
                'networks': ['edge-network'],
                'restart': 'unless-stopped'
            }
        
        compose_config['services'][device_name] = service_config
    
    # Write to file with header comment
    logger.info(f"Writing configuration to {output_file}")
    with open(output_file, 'w') as f:
        f.write(f"# This file is generated by generate-compose.py\n")
        f.write(f"# To regenerate: python3 generate-compose.py --devices {num_devices}")
        if mqtt_enabled:
            f.write(" --mqtt-enabled")
        f.write(f"\n# Number of devices: {num_devices}\n")
        if mqtt_enabled:
            f.write("# MQTT telemetry: enabled\n")
        f.write("\n")
        yaml.dump(compose_config, f, default_flow_style=False, sort_keys=False)
    
    mqtt_status = "with MQTT telemetry" if mqtt_enabled else "without MQTT"
    logger.info(f"✅ Generated {output_file} with {num_devices} edge devices {mqtt_status}")
    return output_file


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Generate docker-compose.yml for IoT edge device simulation with MQTT telemetry"
    )
    parser.add_argument(
        '--devices',
        type=int,
        default=5,
        help='Number of edge devices to create (default: 5)'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='docker-compose.yml',
        help='Output file name (default: docker-compose.yml)'
    )
    parser.add_argument(
        '--mqtt-enabled',
        action='store_true',
        default=True,
        help='Enable MQTT telemetry simulation (default: enabled)'
    )
    parser.add_argument(
        '--no-mqtt',
        action='store_true',
        help='Disable MQTT telemetry (use original simple device simulation)'
    )
    
    args = parser.parse_args()
    
    if args.devices < 1:
        parser.error("Number of devices must be at least 1")
    
    if args.devices > 10000:
        logger.warning(f"Creating {args.devices} devices may consume significant resources")
        response = input("Continue? (yes/no): ")
        if response.lower() not in ['yes', 'y']:
            logger.info("Cancelled by user")
            return
    
    # Determine MQTT mode
    mqtt_enabled = not args.no_mqtt
    
    generate_compose(args.devices, mqtt_enabled, args.output)
    
    print(f"\n📋 Next steps:")
    print(f"   1. Review the generated {args.output}")
    if mqtt_enabled:
        print(f"   2. Ensure config/mosquitto.conf exists for MQTT broker")
        print(f"   3. Run: docker compose up --build")
        print(f"   4. Monitor telemetry: python3 mqtt_consumer.py")
        print(f"\n🔗 MQTT Topics: iot/telemetry/+")
        print(f"🔗 MQTT Broker: localhost:1883")
    else:
        print(f"   2. Customize config/config.json if needed")
        print(f"   3. Run: docker compose up --build")
    print(f"\n📊 Generated {args.devices} devices {'with MQTT telemetry' if mqtt_enabled else 'without MQTT'}")


if __name__ == '__main__':
    main()
