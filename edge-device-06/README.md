# Edge Device 06 Configuration

This folder contains configuration files for edge-device-06.

## Configuration Files

- `config.json`: Main device configuration file
  - Device ID and name
  - Device type (Raspberry Pi 3)
  - Sensor configurations
  - Network settings

## Usage

This configuration is automatically mounted into the Docker container at `/etc/edge-device/`.

You can customize the configuration by editing the files in this folder. The changes will be reflected in the running container after restart.
