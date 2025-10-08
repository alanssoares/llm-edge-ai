# Quick Start Guide - LLM Inference on Edge Devices

This guide will help you quickly set up and run LLM inference on IoT edge devices.

## Prerequisites

- Docker and Docker Compose installed
- At least 8GB RAM available
- 10GB free disk space (for model downloads)
- Python 3.8+ (for utility scripts)

## Quick Start (5 minutes)

### 1. Generate Configuration

```bash
# Generate docker-compose with LLM enabled on device 1
python src/generate_compose.py --devices 3 --enable-llm --llm-devices "1"
```

This creates a docker-compose.yml with:
- 3 edge devices
- LLM inference enabled only on device 1
- Default model: Phi-3.5-mini-instruct

### 2. Start the System

```bash
# Build and start containers
docker compose up --build
```

**Note**: First run will download the model (~7GB), which may take 10-30 minutes depending on your internet connection.

### 3. Monitor the Output

```bash
# In another terminal, watch device 1 logs
docker logs -f edge-device-01

# You should see:
# - "Loading model: microsoft/Phi-3.5-mini-instruct"
# - "Model loaded successfully"
# - Telemetry messages being sent
# - "Running LLM inference..." every 5 messages
# - Inference metrics (time, memory, CPU, energy)
```

### 4. View Analysis Results

```bash
# Subscribe to analysis results via MQTT
docker exec -it mqtt-broker mosquitto_sub -t "iot/analysis/#"

# Subscribe to metrics
docker exec -it mqtt-broker mosquitto_sub -t "iot/metrics/#"
```

### 5. Check Saved Metrics

```bash
# Wait a few minutes, then check metrics files
ls -lh metrics/edge-device-01/

# View latest metrics
cat metrics/edge-device-01/*.json | python -m json.tool
```

## Testing Different Models

### Test 1: Default Model (Phi-3.5)

```bash
# Already running from Quick Start above
# Let it run for 15-30 minutes
docker compose down

# Save results
mkdir -p results/phi35
cp -r metrics/edge-device-01/* results/phi35/
```

### Test 2: TinyLlama (Lightweight)

```bash
# Generate new configuration with TinyLlama
python src/generate_compose.py --devices 3 --enable-llm --llm-devices "1" \
  --llm-model "TinyLlama/TinyLlama-1.1B-Chat-v1.0"

# Start system
docker compose up --build

# Let it run for 15-30 minutes
docker compose down

# Save results
mkdir -p results/tinyllama
cp -r metrics/edge-device-01/* results/tinyllama/
```

### Test 3: Compare Results

```bash
# Use the analysis tool
python scripts/analyze_metrics.py --metrics-dir results --compare

# Export to CSV for Excel/spreadsheet analysis
python scripts/analyze_metrics.py --metrics-dir results --export-csv comparison.csv
```

## Common Scenarios

### Scenario 1: Test Single Device

```bash
# Minimal setup for testing
python src/generate_compose.py --devices 1 --enable-llm
docker compose up --build
```

### Scenario 2: Multiple Devices with Different Models

Edit `docker-compose.yml` manually:

```yaml
edge-device-01:
  environment:
    - ENABLE_LLM=true
    - LLM_MODEL_NAME=microsoft/Phi-3.5-mini-instruct

edge-device-02:
  environment:
    - ENABLE_LLM=true
    - LLM_MODEL_NAME=TinyLlama/TinyLlama-1.1B-Chat-v1.0

edge-device-03:
  environment:
    - ENABLE_LLM=false  # No LLM, just telemetry
```

Then:

```bash
docker compose up --build
```

### Scenario 3: Production-like Setup

```bash
# 10 devices, LLM on 3 devices, less frequent inference
python src/generate_compose.py --devices 10 --enable-llm --llm-devices "1,5,9"

# Edit docker-compose.yml to adjust inference interval
# Change LLM_INFERENCE_INTERVAL=5 to LLM_INFERENCE_INTERVAL=10

docker compose up --build -d  # Run in background
```

## Viewing Real-time Metrics

### Option 1: Docker Logs

```bash
# Watch specific device
docker logs -f edge-device-01 | grep "Inference"

# Watch all LLM activity
docker compose logs -f | grep "LLM"
```

### Option 2: MQTT Subscription

```bash
# All metrics
docker exec -it mqtt-broker mosquitto_sub -t "iot/#" -v

# Just inference metrics
docker exec -it mqtt-broker mosquitto_sub -t "iot/metrics/#" -v

# Just analysis results
docker exec -it mqtt-broker mosquitto_sub -t "iot/analysis/#" -v
```

### Option 3: Python MQTT Consumer

Create `monitor.py`:

```python
import paho.mqtt.client as mqtt
import json

def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload)
        if 'inference_time_ms' in data:
            print(f"Inference: {data['inference_time_ms']:.2f}ms, "
                  f"Memory: {data['memory_used_mb']:.2f}MB, "
                  f"Energy: {data['energy_consumed_mj']:.2f}mJ")
    except:
        pass

client = mqtt.Client()
client.on_message = on_message
client.connect("localhost", 1883)
client.subscribe("iot/metrics/#")
client.loop_forever()
```

Run:
```bash
python monitor.py
```

## Troubleshooting Quick Fixes

### Problem: Out of Memory

```bash
# Use smaller model
python src/generate_compose.py --devices 1 --enable-llm \
  --llm-model "TinyLlama/TinyLlama-1.1B-Chat-v1.0"

# Or increase Docker memory limit
# Edit docker-compose.yml, add under edge-device-01:
#   mem_limit: 4g
```

### Problem: Slow Inference

```bash
# Reduce max token length
# Edit docker-compose.yml, add:
#   - LLM_MAX_LENGTH=256

# Run inference less frequently
#   - LLM_INFERENCE_INTERVAL=10
```

### Problem: Model Download Fails

```bash
# Pre-download on host
pip install transformers torch
python -c "from transformers import AutoModelForCausalLM; AutoModelForCausalLM.from_pretrained('microsoft/Phi-3.5-mini-instruct')"

# Then mount cache in docker-compose.yml:
# volumes:
#   - ~/.cache/huggingface:/root/.cache/huggingface
```

### Problem: Container Crashes

```bash
# Check logs
docker logs edge-device-01

# Check memory usage
docker stats edge-device-01

# Restart specific device
docker compose restart edge-device-01
```

## Understanding the Metrics

### Inference Time
- **Good**: < 1000ms (1 second)
- **Acceptable**: 1000-3000ms
- **Slow**: > 3000ms

### Memory Usage
- **Phi-3.5**: ~3-5GB
- **TinyLlama**: ~1-2GB
- **Overhead**: ~500MB per device

### CPU Usage
- **Normal**: 60-80% during inference
- **High**: 80-95%
- **Problem**: 100% sustained

### Energy Consumption
- **Per inference**: 15-25 mJ (typical)
- **Per hour**: ~300-500 J (5W device)
- **Daily**: ~400-700 kJ

## Next Steps

1. **Experiment with Models**: Try different models from Hugging Face
2. **Tune Parameters**: Adjust temperature, max_length for your use case
3. **Scale Testing**: Test with more devices
4. **Integration**: Connect to your real IoT infrastructure
5. **Analysis**: Use metrics to optimize for your hardware

## Resources

- Full documentation: `docs/LLM_INFERENCE.md`
- Architecture: `ARCHITECTURE.md`
- Model comparison tool: `scripts/analyze_metrics.py`
- Hugging Face models: https://huggingface.co/models

## Getting Help

Check logs:
```bash
docker logs edge-device-01 2>&1 | tail -100
```

Check resource usage:
```bash
docker stats --no-stream
```

Verify MQTT:
```bash
docker exec -it mqtt-broker mosquitto_sub -t "#" -v
```

For more help, see the full documentation or check the logs for error messages.
