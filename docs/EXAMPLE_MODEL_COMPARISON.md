# Example: Docker Compose with Different LLM Models

This example shows how to configure multiple edge devices with different LLM models for comparison.

## Scenario: Comparing 3 Models

- **Device 1**: Phi-3.5-mini-instruct (default, balanced)
- **Device 2**: TinyLlama (lightweight, fast)
- **Device 3**: No LLM (baseline for comparison)

## Configuration

Save this as a custom docker-compose configuration:

```yaml
services:
  mqtt-broker:
    image: eclipse-mosquitto:1.6
    container_name: mqtt-broker
    hostname: mqtt-broker
    ports:
      - 1883:1883
      - 9001:9001
    volumes:
      - ./config/mosquitto.conf:/mosquitto/config/mosquitto.conf:ro
      - mosquitto_data:/mosquitto/data
      - mosquitto_logs:/mosquitto/log
    networks:
      - edge-network
    restart: unless-stopped

  iot-device-image:
    build:
      context: .
      dockerfile: Dockerfile
      args:
        BUILDKIT_INLINE_CACHE: '1'
    image: iot-device-simulator:latest
    command: ['echo', 'This service builds the shared image']

  # Device 1: Phi-3.5-mini-instruct (Default)
  edge-device-01:
    image: iot-device-simulator:latest
    container_name: edge-device-01
    hostname: edge-device-01
    environment:
      - DEVICE_NAME=edge-device-01
      - DEVICE_ID=00:0f:00:70:91:0a
      - MQTT_BROKER=mqtt-broker
      - MQTT_PORT=1883
      # LLM Configuration
      - ENABLE_LLM=true
      - LLM_MODEL_NAME=microsoft/Phi-3.5-mini-instruct
      - LLM_INFERENCE_INTERVAL=5
      - LLM_MAX_LENGTH=512
      - LLM_TEMPERATURE=0.7
    volumes:
      - ./config:/etc/edge-device:ro
      - ./dataset:/app/dataset:ro
      - ./metrics/edge-device-01:/app/metrics
    networks:
      - edge-network
    depends_on:
      - mqtt-broker
      - iot-device-image
    restart: unless-stopped

  # Device 2: TinyLlama (Lightweight)
  edge-device-02:
    image: iot-device-simulator:latest
    container_name: edge-device-02
    hostname: edge-device-02
    environment:
      - DEVICE_NAME=edge-device-02
      - DEVICE_ID=1c:bf:ce:15:ec:4d
      - MQTT_BROKER=mqtt-broker
      - MQTT_PORT=1883
      # LLM Configuration - Lightweight Model
      - ENABLE_LLM=true
      - LLM_MODEL_NAME=TinyLlama/TinyLlama-1.1B-Chat-v1.0
      - LLM_INFERENCE_INTERVAL=5
      - LLM_MAX_LENGTH=512
      - LLM_TEMPERATURE=0.7
    volumes:
      - ./config:/etc/edge-device:ro
      - ./dataset:/app/dataset:ro
      - ./metrics/edge-device-02:/app/metrics
    networks:
      - edge-network
    depends_on:
      - mqtt-broker
      - iot-device-image
    restart: unless-stopped

  # Device 3: No LLM (Baseline)
  edge-device-03:
    image: iot-device-simulator:latest
    container_name: edge-device-03
    hostname: edge-device-03
    environment:
      - DEVICE_NAME=edge-device-03
      - DEVICE_ID=b8:27:eb:bf:9d:51
      - MQTT_BROKER=mqtt-broker
      - MQTT_PORT=1883
      # No LLM - Baseline
      - ENABLE_LLM=false
    volumes:
      - ./config:/etc/edge-device:ro
      - ./dataset:/app/dataset:ro
    networks:
      - edge-network
    depends_on:
      - mqtt-broker
      - iot-device-image
    restart: unless-stopped

volumes:
  mosquitto_data:
    driver: local
  mosquitto_logs:
    driver: local

networks:
  edge-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
```

## Usage

```bash
# Save the above as docker-compose.yml
# Or save as docker-compose-comparison.yml and use:
docker compose -f docker-compose-comparison.yml up --build

# Monitor all devices
docker compose logs -f

# View metrics
docker exec -it mqtt-broker mosquitto_sub -t "iot/metrics/#" -v

# After 30 minutes, compare results
python scripts/analyze_metrics.py --compare
```

## Expected Results

### Device 1 (Phi-3.5)
- Inference Time: ~1500-3000ms
- Memory Usage: ~3-5GB
- Quality: High-quality analysis
- Energy: ~25-40 mJ per inference

### Device 2 (TinyLlama)
- Inference Time: ~500-1500ms
- Memory Usage: ~1-2GB
- Quality: Good analysis (shorter)
- Energy: ~8-20 mJ per inference

### Device 3 (No LLM)
- Inference Time: 0ms
- Memory Usage: ~200MB
- Quality: N/A (raw data only)
- Energy: ~5W baseline

## Monitoring Commands

```bash
# Watch Device 1 (Phi-3.5)
docker logs -f edge-device-01 | grep "Inference"

# Watch Device 2 (TinyLlama)
docker logs -f edge-device-02 | grep "Inference"

# Compare resource usage
docker stats edge-device-01 edge-device-02 edge-device-03

# View analysis results
docker exec -it mqtt-broker mosquitto_sub -t "iot/analysis/#" -v
```

## Analysis

After running for a sufficient time period (30+ minutes):

```bash
# Generate comparison report
python scripts/analyze_metrics.py --metrics-dir metrics --compare --export-csv model_comparison.csv

# View metrics files
cat metrics/edge-device-01/*.json | python -m json.tool
cat metrics/edge-device-02/*.json | python -m json.tool
```

## Alternative Models to Try

Replace `LLM_MODEL_NAME` with:

### Small Models (< 2GB)
- `TinyLlama/TinyLlama-1.1B-Chat-v1.0`
- `stabilityai/stablelm-2-1_6b`

### Medium Models (2-5GB)
- `microsoft/Phi-3-mini-4k-instruct`
- `google/gemma-2b-it`

### Larger Models (5-10GB)
- `microsoft/Phi-3.5-mini-instruct` (default)
- `mistralai/Mistral-7B-Instruct-v0.2`

**Note**: Larger models require more RAM and longer inference times.

## Troubleshooting

### Out of Memory
```yaml
# Add memory limits
edge-device-01:
  mem_limit: 6g
  memswap_limit: 8g
```

### Slow Performance
```yaml
# Reduce inference frequency
- LLM_INFERENCE_INTERVAL=10  # Every 10 messages instead of 5

# Reduce token length
- LLM_MAX_LENGTH=256  # Shorter responses
```

### Model Download Issues
```bash
# Pre-download models
python -c "from transformers import AutoModelForCausalLM; AutoModelForCausalLM.from_pretrained('microsoft/Phi-3.5-mini-instruct')"
python -c "from transformers import AutoModelForCausalLM; AutoModelForCausalLM.from_pretrained('TinyLlama/TinyLlama-1.1B-Chat-v1.0')"
```
