# IoT Device MQTT Simulation

This project simulates IoT devices sending telemetry data via MQTT based on real sensor data from the dataset.

## Architecture

- **MQTT Broker**: Eclipse Mosquitto running on port 1883
- **Device Simulators**: 5 containers simulating IoT devices with real telemetry data
- **Data Source**: Real IoT telemetry dataset with 405,184 records

## Quick Start

### 1. Build the Shared Device Image

```bash
# Build the shared IoT device image (only needs to be done once)
docker-compose --profile build-only up --build iot-device-image

# Or build and start all services at once
docker-compose up --build

# Or run in detached mode
docker-compose up --build -d
```

### 2. Monitor Telemetry Data

You can consume the telemetry data in several ways:

#### Option A: Using the Python Consumer Script

```bash
# Install dependencies
pip install paho-mqtt

# Run the consumer
python3 mqtt_consumer.py
```

#### Option B: Using MQTT Client Tools

```bash
# Using mosquitto_sub (if you have mosquitto-clients installed)
mosquitto_sub -h localhost -t "iot/telemetry/+"

# Using mqtt-cli (if installed)
mqtt sub -h localhost -t "iot/telemetry/+"
```

#### Option C: Using MQTT Explorer (GUI)

1. Download [MQTT Explorer](http://mqtt-explorer.com/)
2. Connect to `localhost:1883`
3. Subscribe to topic `iot/telemetry/+`

## Services

### MQTT Broker
- **Container**: `mqtt-broker`
- **Port**: 1883 (MQTT), 9001 (WebSocket)
- **Configuration**: `config/mosquitto.conf`

### Shared Device Image
- **Image**: `iot-device-simulator:latest`
- **Base**: ARM32v7 Debian (Raspberry Pi compatible)
- **Built once, used by all device containers**

### Device Simulators (using shared image)
- **edge-device-01**: Device ID `00:0f:00:70:91:0a` (stable, cooler, humid)
- **edge-device-02**: Device ID `1c:bf:ce:15:ec:4d` (variable conditions)
- **edge-device-03**: Device ID `b8:27:eb:bf:9d:51` (stable, warmer, dry)
- **edge-device-04**: Device ID `00:0f:00:70:91:0a` (duplicate for load testing)
- **edge-device-05**: Device ID `1c:bf:ce:15:ec:4d` (duplicate for load testing)

## MQTT Topics

- **Pattern**: `iot/telemetry/{device_id}`
- **Examples**:
  - `iot/telemetry/00:0f:00:70:91:0a`
  - `iot/telemetry/1c:bf:ce:15:ec:4d`
  - `iot/telemetry/b8:27:eb:bf:9d:51`

## Message Format

```json
{
  "data": {
    "co": 0.006104480269226063,
    "humidity": 55.099998474121094,
    "light": true,
    "lpg": 0.008895956948783413,
    "motion": false,
    "smoke": 0.023978358312270912,
    "temp": 31.799999237060547
  },
  "device_id": "6e:81:c9:d4:9e:58",
  "ts": 1594419195.292461
}
```

## Data Characteristics

- **Frequency**: 1-5 seconds between messages (randomized)
- **Data Source**: Real IoT telemetry from July 12-19, 2020
- **Sensors**: Temperature, Humidity, CO, LPG, Smoke, Light, Motion
- **Devices**: 3 unique device IDs with different environmental conditions

## Environment Variables

### Device Simulators
- `DEVICE_NAME`: Name of the device container
- `DEVICE_ID`: MAC address of the simulated device
- `MQTT_BROKER`: MQTT broker hostname (default: mqtt-broker)
- `MQTT_PORT`: MQTT broker port (default: 1883)

### MQTT Consumer
- `MQTT_BROKER`: MQTT broker hostname (default: localhost)
- `MQTT_PORT`: MQTT broker port (default: 1883)

## Monitoring and Logs

### View Device Logs
```bash
# View logs for a specific device
docker-compose logs -f edge-device-01

# View logs for all devices
docker-compose logs -f
```

### View MQTT Broker Logs
```bash
# View MQTT broker logs
docker-compose logs -f mqtt-broker
```

### Check Container Status
```bash
# Check running containers
docker-compose ps

# Check resource usage
docker stats
```

## Stopping the Simulation

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (clears MQTT data)
docker-compose down -v
```

## Troubleshooting

### Common Issues

1. **Port 1883 already in use**
   ```bash
   # Check what's using the port
   netstat -tulpn | grep 1883
   
   # Kill the process or change the port in docker-compose.yml
   ```

2. **Device not connecting to MQTT**
   ```bash
   # Check if MQTT broker is running
   docker-compose ps mqtt-broker
   
   # Check MQTT broker logs
   docker-compose logs mqtt-broker
   ```

3. **No telemetry data received**
   ```bash
   # Check if devices are running
   docker-compose ps
   
   # Check device logs
   docker-compose logs edge-device-01
   ```

### Testing MQTT Connection

```bash
# Test MQTT broker connectivity
docker exec -it mqtt-broker mosquitto_pub -h localhost -t "test/topic" -m "Hello World"

# Test subscription
docker exec -it mqtt-broker mosquitto_sub -h localhost -t "test/topic"
```

## Integration Examples

### Python Consumer
```python
import paho.mqtt.client as mqtt
import json

def on_message(client, userdata, msg):
    data = json.loads(msg.payload.decode())
    print(f"Device: {data['device_id']}, Temp: {data['data']['temp']}°F")

client = mqtt.Client()
client.on_message = on_message
client.connect("localhost", 1883, 60)
client.subscribe("iot/telemetry/+")
client.loop_forever()
```

### Node.js Consumer
```javascript
const mqtt = require('mqtt');
const client = mqtt.connect('mqtt://localhost:1883');

client.on('connect', () => {
    client.subscribe('iot/telemetry/+');
});

client.on('message', (topic, message) => {
    const data = JSON.parse(message.toString());
    console.log(`Device: ${data.device_id}, Temp: ${data.data.temp}°F`);
});
```

## Performance Notes

- Each device sends ~12-20 messages per minute
- Total system throughput: ~60-100 messages per minute
- MQTT broker can handle 1000+ concurrent connections
- Data persistence enabled for reliability
