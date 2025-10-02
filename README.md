# llm-edge-ai
A simulation of local devices as raspberry phi with sensors

## Overview

This project simulates a network of 10 Raspberry Pi 3 devices using Docker Compose. Each device runs in its own container on an internal network, allowing for testing and development of edge computing scenarios.

## Architecture

- **10 Edge Devices**: Simulated Raspberry Pi 3 devices (edge-device-01 through edge-device-10)
- **Internal Network**: All devices connected via a bridge network (172.20.0.0/16)
- **Individual Configuration**: Each device has its own configuration folder

## Prerequisites

- Docker Engine (version 20.10 or later)
- Docker Compose (version 1.29 or later)
- At least 4GB of available RAM
- At least 10GB of free disk space

## Quick Start

1. **Build and start all devices:**
   ```bash
   docker-compose up -d
   ```

2. **View running devices:**
   ```bash
   docker-compose ps
   ```

3. **Check logs of a specific device:**
   ```bash
   docker-compose logs edge-device-01
   ```

4. **Access a device shell:**
   ```bash
   docker exec -it edge-device-01 /bin/bash
   ```

5. **Stop all devices:**
   ```bash
   docker-compose down
   ```

## Device Configuration

Each device has its own configuration folder (`edge-device-01` through `edge-device-10`) containing:

- `config.json`: Main device configuration
- `README.md`: Device-specific documentation

### Configuration Structure

```json
{
  "device_id": "01",
  "device_name": "edge-device-01",
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
      "type": "motion",
      "enabled": true
    }
  ],
  "network": {
    "hostname": "edge-device-01",
    "internal_network": "edge-network"
  }
}
```

## Network Configuration

All devices are connected to the `edge-network` internal network:

- **Network Type**: Bridge
- **Subnet**: 172.20.0.0/16
- **Communication**: Devices can communicate with each other using their hostnames

### Testing Network Connectivity

From within any device, you can ping other devices:

```bash
docker exec -it edge-device-01 ping edge-device-02
```

## Management Commands

### Start specific devices:
```bash
docker-compose up -d edge-device-01 edge-device-02
```

### Restart a device:
```bash
docker-compose restart edge-device-01
```

### View real-time logs:
```bash
docker-compose logs -f edge-device-01
```

### Scale devices (add more):
To add more devices, edit `docker-compose.yml` and add new service definitions following the existing pattern.

## Customization

### Modifying Device Configuration

1. Edit the configuration files in the respective `edge-device-XX` folder
2. Restart the specific device:
   ```bash
   docker-compose restart edge-device-01
   ```

### Adding Custom Scripts

You can add custom scripts to device folders, and they will be available at `/etc/edge-device/` inside the containers.

## Troubleshooting

### Containers not starting
- Check Docker resources: `docker system df`
- Verify Docker Compose version: `docker-compose --version`
- Check logs: `docker-compose logs`

### Network issues
- Verify network exists: `docker network ls | grep edge-network`
- Check network configuration: `docker network inspect edge-network`

## License

Apache License 2.0
