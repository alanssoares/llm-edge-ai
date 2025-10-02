# llm-edge-ai
A simulation of local devices as raspberry phi with sensors

## Overview

This project simulates a scalable network of Raspberry Pi 3 devices using Docker Compose. The setup can scale from a few devices to thousands, making it perfect for testing and development of edge computing scenarios.

## Key Features

- **Scalable Architecture**: Easily configure 10 to 1000+ devices
- **Dynamic Generation**: Python script generates docker-compose.yml for any number of devices
- **Shared Configuration**: Single configuration file shared across all devices
- **Internal Network**: All devices connected via a bridge network (172.20.0.0/16)
- **No Per-Device Folders**: Simplified structure that scales efficiently

## Prerequisites

- Docker Engine (version 20.10 or later)
- Docker Compose (version 1.29 or later)
- Python 3 (for generating docker-compose.yml)
- PyYAML: `pip3 install pyyaml`

## Quick Start

### 1. Generate docker-compose.yml

Generate a configuration with your desired number of devices:

```bash
# Generate with 10 devices (default)
python3 generate-compose.py --devices 10

# Generate with 50 devices
python3 generate-compose.py --devices 50

# Generate with 1000 devices
python3 generate-compose.py --devices 1000
```

Or use the Makefile:

```bash
# Generate with 10 devices
make generate

# Generate with 100 devices
make generate DEVICES=100
```

### 2. Start the devices

```bash
# Start all devices
docker compose up -d

# Or use make
make up
```

### 3. Verify and interact

```bash
# View running devices
docker compose ps

# Check logs of a specific device
docker compose logs edge-device-01

# Access a device shell
docker exec -it edge-device-01 /bin/bash

# Stop all devices
docker compose down
```

## Configuration

### Shared Configuration

All devices share the same base configuration located in `config/config.json`:

```json
{
  "device_type": "raspberry-pi-3",
  "sensors": [
    {
      "type": "temperature",
      "unit": "celsius",
      "enabled": true
    },
    {
      "type": "humidity",
      "unit": "percent",
      "enabled": true
    },
    {
      "type": "pressure",
      "unit": "hPa",
      "enabled": true
    },
    {
      "type": "light",
      "unit": "lux",
      "enabled": true
    }
  ],
  "network": {
    "internal_network": "edge-network"
  }
}
```

### Device-Specific Settings

Each device receives unique identifiers via environment variables:
- `DEVICE_NAME`: Unique device name (e.g., edge-device-01)
- `DEVICE_ID`: Unique device ID (e.g., 01)

These are automatically set when generating the docker-compose.yml.

## Network Configuration

All devices are connected to the `edge-network` internal network:

- **Network Type**: Bridge
- **Subnet**: 172.20.0.0/16
- **Communication**: Devices can communicate with each other using their hostnames

### Testing Network Connectivity

```bash
docker exec -it edge-device-01 ping edge-device-02
```

## Scaling

### Small Scale (10-100 devices)
Perfect for development and testing:
```bash
make generate DEVICES=50
make up
```

### Medium Scale (100-500 devices)
Suitable for integration testing:
```bash
make generate DEVICES=200
make up
```

### Large Scale (500-1000+ devices)
For stress testing and performance evaluation:
```bash
make generate DEVICES=1000
make up
```

**Note**: Large numbers of containers require significant system resources. Monitor Docker resource usage.

## Management Commands

### Using Makefile

```bash
make help                    # Show all available commands
make generate DEVICES=N      # Generate docker-compose.yml with N devices
make build                   # Build all edge device images
make up                      # Start all edge devices
make down                    # Stop all edge devices
make restart                 # Restart all edge devices
make logs                    # View logs from all devices
make ps                      # Show status of all devices
make clean                   # Remove all containers and images
```

### Using Docker Compose Directly

```bash
# Start specific devices
docker compose up -d edge-device-01 edge-device-02

# Restart a device
docker compose restart edge-device-01

# View real-time logs
docker compose logs -f edge-device-01

# Stop specific devices
docker compose stop edge-device-01
```

## Customization

### Modifying Shared Configuration

1. Edit `config/config.json` with your desired settings
2. Restart devices to apply changes:
   ```bash
   make restart
   ```

### Customizing Device Generation

Edit `generate-compose.py` to customize:
- Resource limits (CPU, memory)
- Additional environment variables
- Different volume mounts
- Custom networks or security settings

### Adding Custom Scripts

Add scripts to the `config/` directory. They will be available at `/etc/edge-device/` inside all containers (mounted read-only).

## Troubleshooting

### Containers not starting
- Check Docker resources: `docker system df`
- Verify Docker Compose version: `docker compose version`
- Check logs: `docker compose logs`
- Reduce number of devices if running into resource limits

### Network issues
- Verify network exists: `docker network ls | grep edge-network`
- Check network configuration: `docker network inspect edge-network`

### Generation script issues
- Ensure PyYAML is installed: `pip3 install pyyaml`
- Check Python version: `python3 --version` (requires 3.6+)

## License

Apache License 2.0
