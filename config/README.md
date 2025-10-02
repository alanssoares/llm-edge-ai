# Shared Configuration

This directory contains the shared configuration for all edge devices.

## Configuration Files

- `config.json`: Base configuration shared across all devices
  - Device type (Raspberry Pi 3)
  - Sensor configurations
  - Network settings

## Device-Specific Configuration

Device-specific settings are provided through environment variables:
- `DEVICE_NAME`: Unique device name (e.g., edge-device-01)
- `DEVICE_ID`: Unique device ID (e.g., 01)

These are automatically set by the docker-compose configuration.

## Customization

To customize the configuration for all devices, edit `config.json` in this directory.
The changes will be reflected in all containers (note: configuration is mounted read-only).

To have device-specific configurations, you can:
1. Modify the `generate-compose.py` script to use device-specific config volumes
2. Use environment variables in your application to customize behavior per device
3. Create a configuration service that devices query at startup
