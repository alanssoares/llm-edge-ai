# llm-edge-ai
A simulation of local edge devices (Raspberry Pi) with IoT sensors and integrated LLM inference capabilities

## Overview

This project simulates a scalable network of Raspberry Pi 3 devices using Docker Compose. The setup can scale from a few devices to thousands, making it perfect for testing and development of edge computing scenarios. Now includes **on-device LLM inference** for intelligent IoT data analysis with comprehensive performance metrics.

## Key Features

- **Scalable Architecture**: Easily configure 10 to 1000+ devices
- **MQTT Telemetry**: Real-time sensor data streaming via MQTT
- **🤖 LLM Inference on Edge**: Run Phi-3.5-mini-instruct or other models directly on each device
- **📊 Performance Metrics**: Track inference time, memory usage, CPU utilization, and energy consumption
- **🔄 Model Comparison**: Test and compare different LLM models for edge deployment
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

### Basic Setup (Without LLM)

```bash
# Generate configuration with 5 devices
python src/generate_compose.py --devices 5

# Start all devices
docker compose up -d

# View running devices
docker compose ps

# Monitor MQTT telemetry
python src/mqtt_consumer.py

# Stop all devices
docker compose down
```

### 🤖 Quick Start with LLM Inference

```bash
# Generate configuration with LLM enabled on device 1
python src/generate_compose.py --devices 3 --enable-llm --llm-devices "1"

# Start the system (first run downloads model ~7GB)
docker compose up --build

# In another terminal, monitor LLM analysis
docker exec -it mqtt-broker mosquitto_sub -t "iot/analysis/#"

# View metrics
cat metrics/edge-device-01/*.json
```

**For detailed LLM setup and model comparison guide, see [docs/QUICKSTART_LLM.md](docs/QUICKSTART_LLM.md)**

### Standard Device Interaction

```bash
# Check logs of a specific device
docker compose logs edge-device-01

# Follow logs in real-time
docker logs -f edge-device-01

# Access a device shell
docker exec -it edge-device-01 /bin/bash

# View resource usage
docker stats edge-device-01
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
- `DEVICE_ID`: Unique device ID (MAC address from dataset)
- `MQTT_BROKER`: MQTT broker hostname
- `MQTT_PORT`: MQTT broker port

### LLM Configuration

Enable and configure LLM inference per device:
- `ENABLE_LLM`: Set to `true` to enable LLM inference
- `LLM_MODEL_NAME`: Hugging Face model identifier (default: `microsoft/Phi-3.5-mini-instruct`)
- `LLM_INFERENCE_INTERVAL`: Run inference every N messages (default: 5)
- `LLM_MAX_LENGTH`: Maximum token length (default: 512)
- `LLM_TEMPERATURE`: Sampling temperature (default: 0.7)

These are automatically set when generating the docker-compose.yml with `--enable-llm` flag.

## LLM Inference Features

### Supported Models

The system supports any Hugging Face causal language model. Tested models:
- **Phi-3.5-mini-instruct** (default) - Optimized for edge, ~7B params
- **TinyLlama-1.1B** - Lightweight for resource-constrained devices
- **Phi-3-mini-4k** - Compact variant of Phi-3
- **Gemma-2b** - Google's efficient small model

### Performance Metrics

Each inference automatically collects:
- ⏱️ **Inference Time**: Milliseconds per inference
- 💾 **Memory Usage**: RAM consumption in MB
- 🖥️ **CPU Utilization**: Average CPU percentage during inference
- ⚡ **Energy Consumption**: Estimated energy in millijoules

### Comparing Models

```bash
# Test Phi-3.5
python src/generate_compose.py --devices 1 --enable-llm --llm-model "microsoft/Phi-3.5-mini-instruct"
docker compose up --build
# Let run for 30 minutes, then: docker compose down

# Test TinyLlama
python src/generate_compose.py --devices 1 --enable-llm --llm-model "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
docker compose up --build
# Let run for 30 minutes, then: docker compose down

# Compare results
python scripts/analyze_metrics.py --compare --export-csv comparison.csv
```

### MQTT Topics

When LLM is enabled, additional topics are available:
- `iot/telemetry/{device_id}` - Raw sensor data
- `iot/analysis/{device_id}` - LLM analysis results
- `iot/metrics/{device_id}` - Inference performance metrics
- `iot/metrics/{device_id}/summary` - Aggregated statistics

### Documentation

- **[Quick Start Guide](docs/QUICKSTART_LLM.md)** - Get started with LLM in 5 minutes
- **[Full LLM Documentation](docs/LLM_INFERENCE.md)** - Complete guide to LLM features
- **[Metrics Analysis Tool](scripts/analyze_metrics.py)** - Compare model performance

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
python3 scripts/generate-compose.py --devices 50
docker compose up -d
```

### Medium Scale (100-500 devices)
Suitable for integration testing:
```bash
python3 scripts/generate-compose.py --devices 200
docker compose up -d
```

### Large Scale (500-1000+ devices)
For stress testing and performance evaluation:
```bash
python3 scripts/generate-compose.py --devices 1000
docker compose up -d
```

**Note**: Large numbers of containers require significant system resources. Monitor Docker resource usage.

## Management Commands

### Using Docker Compose

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

## Project Structure

```
llm-edge-ai/
├── src/                        # Source code
│   ├── device_simulator.py     # IoT device simulator with LLM
│   ├── llm_inference.py        # LLM inference engine
│   ├── mqtt_consumer.py        # MQTT telemetry consumer
│   └── generate_compose.py     # Docker compose generator with LLM support
├── scripts/                    # Utility scripts
│   ├── generate-compose.py     # Entry point for compose generation
│   └── analyze_metrics.py      # LLM metrics analysis and comparison
├── tests/                      # Unit tests
├── config/                     # Configuration files
│   ├── config.json             # Device configuration
│   └── mosquitto.conf          # MQTT broker configuration
├── dataset/                    # IoT telemetry dataset
│   └── iot_telemetry_data.csv  # Real sensor data
├── docs/                       # Documentation
│   ├── QUICKSTART_LLM.md       # Quick start guide for LLM
│   ├── LLM_INFERENCE.md        # Complete LLM documentation
│   └── MQTT_SIMULATION.md      # MQTT setup guide
├── metrics/                    # LLM inference metrics (generated)
│   └── edge-device-XX/         # Per-device metrics
├── requirements.txt            # Python dependencies (including LLM)
└── docker-compose.yml          # Generated compose file
```

## Customization

### Modifying Shared Configuration

1. Edit `config/config.json` with your desired settings
2. Restart devices to apply changes:
   ```bash
   docker compose restart
   ```

### Customizing Device Generation

Edit `src/generate_compose.py` to customize:
- Resource limits (CPU, memory)
- Additional environment variables
- Different volume mounts
- Custom networks or security settings

### Adding Custom Scripts

Add scripts to the `config/` directory. They will be available at `/etc/edge-device/` inside all containers (mounted read-only).

## Development

### Running Tests

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_simulator.py
```

### Code Formatting

```bash
# Format code with Black
black src/ tests/

# Sort imports
isort src/ tests/

# Check linting
flake8 src/ tests/
```

### Environment Variables

Copy `.env.example` to `.env` and customize:

```bash
cp .env.example .env
```

Available variables:
- `DEVICE_NAME`: Device identifier
- `DEVICE_ID`: MAC address format
- `MQTT_BROKER`: Broker hostname
- `MQTT_PORT`: Broker port (default: 1883)
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)

## Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Documentation

- [Architecture](ARCHITECTURE.md) - System architecture and design
- [MQTT Simulation](docs/MQTT_SIMULATION.md) - MQTT simulation details
- [Changelog](CHANGELOG.md) - Version history
- [Contributing](CONTRIBUTING.md) - How to contribute

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
