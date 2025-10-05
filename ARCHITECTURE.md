# Architecture

## Overview

LLM Edge AI is a scalable IoT edge device simulation platform built with Python, Docker, and MQTT. It simulates hundreds to thousands of Raspberry Pi devices sending real telemetry data over MQTT.

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Docker Host                               │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │              Edge Network (172.20.0.0/16)                  │ │
│  │                                                              │ │
│  │  ┌─────────────┐                                            │ │
│  │  │MQTT Broker  │◄───────┐                                  │ │
│  │  │(Mosquitto)  │        │                                   │ │
│  │  │Port: 1883   │        │                                   │ │
│  │  └─────────────┘        │                                   │ │
│  │         ▲                │                                   │ │
│  │         │                │                                   │ │
│  │         │  Telemetry     │  Telemetry                       │ │
│  │         │  Messages      │  Messages                        │ │
│  │         │                │                                   │ │
│  │  ┌──────┴──────┐  ┌─────┴──────┐  ┌──────────────┐        │ │
│  │  │Edge Device  │  │Edge Device │  │Edge Device   │  ...   │ │
│  │  │   #001      │  │   #002     │  │   #NNN       │        │ │
│  │  │             │  │            │  │              │        │ │
│  │  │• Sensors    │  │• Sensors   │  │• Sensors     │        │ │
│  │  │• Dataset    │  │• Dataset   │  │• Dataset     │        │ │
│  │  │• Publisher  │  │• Publisher │  │• Publisher   │        │ │
│  │  └─────────────┘  └────────────┘  └──────────────┘        │ │
│  │                                                              │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                    External Access                          │ │
│  │                                                              │ │
│  │  ┌──────────────┐                                           │ │
│  │  │MQTT Consumer │  Monitors all telemetry                  │ │
│  │  │(localhost)   │◄─────────────────────────────────────────┤ │
│  │  └──────────────┘         Port 1883                        │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## Components

### 1. IoT Device Simulator (`src/device_simulator.py`)

**Purpose**: Simulates individual IoT edge devices

**Key Features**:
- Reads real sensor data from CSV dataset
- Publishes telemetry via MQTT
- Supports multiple sensor types (temp, humidity, CO, LPG, smoke, light, motion)
- Cycles through dataset for realistic patterns
- Configurable via environment variables

**Data Flow**:
1. Load dataset on startup
2. Filter data for specific device ID
3. Connect to MQTT broker
4. Loop through data, publishing at intervals
5. Handle reconnection and errors

### 2. MQTT Consumer (`src/mqtt_consumer.py`)

**Purpose**: Monitors and displays telemetry from all devices

**Key Features**:
- Subscribes to wildcard topic `iot/telemetry/+`
- Displays formatted telemetry data
- Handles JSON parsing and validation
- Provides real-time monitoring

### 3. Docker Compose Generator (`src/generate_compose.py`)

**Purpose**: Dynamically generates docker-compose.yml for any number of devices

**Key Features**:
- Configurable device count (1 to 10,000+)
- Automatic device ID assignment from real dataset
- Network configuration
- Volume management
- MQTT broker setup

**Algorithm**:
```python
for device_number in range(1, num_devices + 1):
    device_id = real_device_ids[device_number % 3]
    create_service(device_id, device_number)
```

### 4. MQTT Broker (Eclipse Mosquitto)

**Purpose**: Message broker for pub/sub communication

**Configuration**:
- Port 1883: MQTT protocol
- Port 9001: WebSocket (optional)
- Persistent volumes for data and logs

## Data Model

### Telemetry Message Format

```json
{
    "device_id": "00:0f:00:70:91:0a",
    "ts": 1594512000.0,
    "data": {
        "temp": 86.0,
        "humidity": 51.0,
        "co": 0.0045,
        "lpg": 0.0076,
        "smoke": 0.0234,
        "light": false,
        "motion": false
    }
}
```

### MQTT Topics

- Pattern: `iot/telemetry/{device_id}`
- QoS: 1 (at least once delivery)
- Retained: No

## Scalability

### Small Scale (10-100 devices)
- Resource usage: Low (~1-2 GB RAM)
- Use case: Development, testing
- Startup time: < 30 seconds

### Medium Scale (100-500 devices)
- Resource usage: Medium (~2-8 GB RAM)
- Use case: Integration testing
- Startup time: 1-2 minutes

### Large Scale (500-1000+ devices)
- Resource usage: High (8+ GB RAM)
- Use case: Stress testing, performance evaluation
- Startup time: 2-5 minutes
- Considerations: Docker resource limits, network bandwidth

### Optimization Strategies

1. **Shared Image**: Single Docker image for all devices
2. **Read-only Volumes**: Configuration and dataset mounted read-only
3. **Bridge Network**: Efficient internal communication
4. **BuildKit Cache**: Faster rebuilds
5. **Lazy Loading**: Devices start independently

## Configuration Management

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DEVICE_NAME` | Device hostname | `edge-device` |
| `DEVICE_ID` | MAC address | `00:0f:00:70:91:0a` |
| `MQTT_BROKER` | Broker hostname | `mqtt-broker` |
| `MQTT_PORT` | Broker port | `1883` |
| `LOG_LEVEL` | Logging level | `INFO` |

### Configuration Files

- `config/config.json`: Shared device configuration
- `config/mosquitto.conf`: MQTT broker configuration
- `.env`: Environment-specific settings

## Security Considerations

### Current Implementation

- Internal Docker network (172.20.0.0/16)
- Non-root container user
- Read-only volume mounts
- No authentication (development only)

### Production Recommendations

- Enable MQTT authentication (username/password)
- Use TLS/SSL encryption
- Implement access control lists (ACLs)
- Add network policies
- Use secrets management
- Enable audit logging

## Monitoring and Observability

### Current Tools

- Docker Compose logs: `docker compose logs -f`
- MQTT Consumer: Real-time telemetry display
- Container stats: `docker stats`

### Future Enhancements

- Prometheus metrics export
- Grafana dashboards
- Centralized logging (ELK stack)
- Alert management
- Performance metrics

## Technology Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| Language | Python | 3.11+ |
| Container | Docker | 20.10+ |
| Orchestration | Docker Compose | 1.29+ |
| Message Broker | Eclipse Mosquitto | 1.6 |
| MQTT Client | Paho MQTT | 1.6.1 |
| Data Processing | Pandas | 1.5.3 |
| Testing | Pytest | 7.4.0+ |

## Design Patterns

### 1. Observer Pattern
- MQTT pub/sub model
- Devices publish, consumers subscribe
- Loose coupling between components

### 2. Factory Pattern
- Docker Compose generator creates device configurations
- Template-based service generation

### 3. Singleton Pattern
- MQTT broker (single instance)
- Shared Docker image

### 4. Strategy Pattern
- Configurable MQTT/no-MQTT modes
- Different device ID assignment strategies

## Performance Characteristics

### Throughput
- Single device: ~0.2-1 msg/sec
- 100 devices: ~20-100 msg/sec
- 1000 devices: ~200-1000 msg/sec

### Latency
- MQTT message delivery: < 10ms (local network)
- Device startup: 2-5 seconds
- Compose generation: < 1 second per 100 devices

### Resource Usage (per device)
- Memory: ~50-100 MB
- CPU: ~0.01 core
- Network: ~1-5 KB/sec

## Future Architecture Enhancements

1. **Kubernetes Support**: Helm charts for K8s deployment
2. **Distributed Broker**: MQTT broker clustering
3. **Data Persistence**: Time-series database integration
4. **Real-time Analytics**: Stream processing (Apache Kafka)
5. **Web Dashboard**: React-based monitoring UI
6. **ML Integration**: Anomaly detection, predictive maintenance
7. **API Gateway**: REST/GraphQL API for device management
