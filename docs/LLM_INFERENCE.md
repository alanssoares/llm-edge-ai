# LLM Inference on Edge Devices

This document describes how to run Large Language Models (LLMs) on IoT edge devices for intelligent telemetry analysis with comprehensive performance metrics.

## Overview

The edge device simulator now supports running LLM inference directly on each device to analyze telemetry data in real-time. This enables:

- **Edge AI Processing**: Analyze sensor data locally without cloud dependency
- **Performance Metrics**: Track inference time, memory usage, and energy consumption
- **Model Comparison**: Test different models to compare efficiency
- **Real-time Analysis**: Generate insights from IoT telemetry data

## Supported Models

The system uses Hugging Face Transformers and supports any compatible causal language model. Default and recommended models:

### Default Model
- **Phi-3.5-mini-instruct** (`microsoft/Phi-3.5-mini-instruct`)
  - Optimized for edge devices
  - ~7B parameters
  - Good balance of performance and resource usage

### Alternative Models
You can use any Hugging Face model via the `LLM_MODEL_NAME` environment variable:

- `microsoft/Phi-3-mini-4k-instruct` - Smaller, faster variant
- `TinyLlama/TinyLlama-1.1B-Chat-v1.0` - Very lightweight for testing
- `google/gemma-2b-it` - Google's compact model
- `stabilityai/stablelm-2-1_6b` - Stability AI's efficient model

## Configuration

### Environment Variables

Configure LLM behavior using environment variables in docker-compose.yml:

```yaml
environment:
  # Enable LLM inference
  - ENABLE_LLM=true
  
  # Model selection (changeable for comparison)
  - LLM_MODEL_NAME=microsoft/Phi-3.5-mini-instruct
  
  # Inference frequency (run every N messages)
  - LLM_INFERENCE_INTERVAL=5
  
  # Model parameters
  - LLM_MAX_LENGTH=512
  - LLM_TEMPERATURE=0.7
```

### Key Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `ENABLE_LLM` | `false` | Enable/disable LLM inference |
| `LLM_MODEL_NAME` | `microsoft/Phi-3.5-mini-instruct` | Hugging Face model identifier |
| `LLM_INFERENCE_INTERVAL` | `5` | Run inference every N telemetry messages |
| `LLM_MAX_LENGTH` | `512` | Maximum token length for generation |
| `LLM_TEMPERATURE` | `0.7` | Sampling temperature (0.0-1.0) |

## Usage

### Generating Docker Compose with LLM

Use the `generate_compose.py` script with LLM options:

```bash
# Enable LLM on all devices
python src/generate_compose.py --devices 5 --enable-llm

# Enable LLM on specific devices only
python src/generate_compose.py --devices 5 --enable-llm --llm-devices "1,3,5"

# Use a different model
python src/generate_compose.py --devices 3 --enable-llm --llm-model "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
```

### Manual Configuration

Edit `docker-compose.yml` and add LLM environment variables to specific devices:

```yaml
edge-device-01:
  image: iot-device-simulator:latest
  environment:
    - DEVICE_NAME=edge-device-01
    - DEVICE_ID=00:0f:00:70:91:0a
    - MQTT_BROKER=mqtt-broker
    - MQTT_PORT=1883
    - ENABLE_LLM=true
    - LLM_MODEL_NAME=microsoft/Phi-3.5-mini-instruct
    - LLM_INFERENCE_INTERVAL=5
  volumes:
    - ./config:/etc/edge-device:ro
    - ./dataset:/app/dataset:ro
    - ./metrics/edge-device-01:/app/metrics
```

### Running the System

```bash
# Build and start containers
docker compose up --build

# View logs from a specific device
docker logs -f edge-device-01

# View all device logs
docker compose logs -f
```

## Metrics Collection

The system automatically collects comprehensive metrics for each inference:

### Inference Metrics

Each inference generates the following metrics:

```json
{
  "timestamp": "2025-10-07T10:30:15.123456",
  "device_id": "00:0f:00:70:91:0a",
  "model_name": "microsoft/Phi-3.5-mini-instruct",
  "inference_time_seconds": 1.2345,
  "inference_time_ms": 1234.5,
  "memory_used_mb": 45.67,
  "memory_total_mb": 512.34,
  "cpu_percent_avg": 78.5,
  "cpu_percent_samples": 24,
  "energy_consumed_mj": 18.75,
  "energy_consumed_j": 0.0188,
  "compute_device": "cpu",
  "prompt_length": 256,
  "response_length": 128
}
```

### Metric Descriptions

| Metric | Unit | Description |
|--------|------|-------------|
| `inference_time_ms` | milliseconds | Time taken for model inference |
| `memory_used_mb` | megabytes | Memory consumed during inference |
| `memory_total_mb` | megabytes | Total memory usage of the process |
| `cpu_percent_avg` | percentage | Average CPU utilization during inference |
| `energy_consumed_mj` | millijoules | Estimated energy consumption |
| `compute_device` | string | Computing device used (cpu/cuda) |

### Energy Consumption Estimation

Energy is estimated based on:
- **Base Power**: ~5W (idle edge device)
- **Max Power**: ~15W (under full load)
- **CPU Utilization**: Dynamic power based on usage
- **Time**: Inference duration

Formula: `Energy (mJ) = [Base + (Max - Base) × CPU%] × Time × 1000`

### Accessing Metrics

#### 1. MQTT Topics

Subscribe to real-time metrics via MQTT:

```bash
# Individual inference metrics
mosquitto_sub -h localhost -t "iot/metrics/+"

# Metrics summaries
mosquitto_sub -h localhost -t "iot/metrics/+/summary"

# Analysis results
mosquitto_sub -h localhost -t "iot/analysis/+"
```

#### 2. JSON Files

Metrics are saved to persistent volumes:

```bash
# View metrics for a specific device
cat metrics/edge-device-01/inference_metrics_*.json

# View all metrics
find metrics/ -name "*.json" -exec cat {} \;
```

#### 3. Summary Statistics

Each metrics file includes a summary section:

```json
{
  "summary": {
    "device_id": "00:0f:00:70:91:0a",
    "model_name": "microsoft/Phi-3.5-mini-instruct",
    "total_inferences": 10,
    "inference_time_ms": {
      "min": 1150.23,
      "max": 1389.45,
      "avg": 1234.56
    },
    "memory_usage_mb": {
      "min": 42.5,
      "max": 48.2,
      "avg": 45.3
    },
    "cpu_usage_percent": {
      "min": 72.1,
      "max": 85.4,
      "avg": 78.5
    },
    "energy_consumption_mj": {
      "min": 17.2,
      "max": 20.8,
      "avg": 18.5,
      "total": 185.0
    }
  }
}
```

## Model Comparison

To compare different models, run the same workload with different configurations:

### Step 1: Test with Phi-3.5

```bash
python src/generate_compose.py --devices 1 --enable-llm --llm-model "microsoft/Phi-3.5-mini-instruct"
docker compose up --build
# Let it run for 30 minutes
docker compose down
# Save metrics: cp metrics/edge-device-01/*.json results/phi35/
```

### Step 2: Test with TinyLlama

```bash
python src/generate_compose.py --devices 1 --enable-llm --llm-model "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
docker compose up --build
# Let it run for 30 minutes
docker compose down
# Save metrics: cp metrics/edge-device-01/*.json results/tinyllama/
```

### Step 3: Compare Results

Create a comparison script:

```python
import json
import glob

def compare_models(model_dirs):
    for model_name, metrics_dir in model_dirs.items():
        files = glob.glob(f"{metrics_dir}/*.json")
        if files:
            with open(files[0], 'r') as f:
                data = json.load(f)
                summary = data['summary']
                
                print(f"\n{model_name}:")
                print(f"  Avg Inference Time: {summary['inference_time_ms']['avg']:.2f} ms")
                print(f"  Avg Memory Usage: {summary['memory_usage_mb']['avg']:.2f} MB")
                print(f"  Avg CPU Usage: {summary['cpu_usage_percent']['avg']:.2f}%")
                print(f"  Total Energy: {summary['energy_consumption_mj']['total']:.2f} mJ")

compare_models({
    "Phi-3.5-mini": "results/phi35",
    "TinyLlama": "results/tinyllama"
})
```

## Performance Optimization

### For CPU-only Devices

```yaml
environment:
  - LLM_MAX_LENGTH=256  # Reduce max tokens
  - LLM_TEMPERATURE=0.3  # Lower temperature for faster inference
  - LLM_INFERENCE_INTERVAL=10  # Run less frequently
```

### For GPU-enabled Devices

The system automatically detects and uses CUDA if available:

```bash
# Check if GPU is being used in logs
docker logs edge-device-01 | grep "Compute device"
# Should show: "Compute device: cuda"
```

### Memory Constraints

For devices with limited memory:

1. Use smaller models (TinyLlama, Phi-3-mini)
2. Reduce `LLM_MAX_LENGTH`
3. Increase `LLM_INFERENCE_INTERVAL`

## Troubleshooting

### Model Download Issues

**Problem**: Model download fails or times out

**Solution**:
```bash
# Pre-download model on host machine
pip install transformers torch
python -c "from transformers import AutoModelForCausalLM; AutoModelForCausalLM.from_pretrained('microsoft/Phi-3.5-mini-instruct')"

# Then mount the cache in docker-compose.yml
volumes:
  - ~/.cache/huggingface:/root/.cache/huggingface
```

### Out of Memory

**Problem**: Container crashes with OOM error

**Solution**:
```yaml
# Increase memory limit in docker-compose.yml
edge-device-01:
  mem_limit: 4g
  memswap_limit: 6g
```

### Slow Inference

**Problem**: Inference takes too long

**Solutions**:
1. Use a smaller model
2. Reduce `LLM_MAX_LENGTH`
3. Use quantized models (future enhancement)
4. Enable GPU if available

## Example Output

### Telemetry Analysis

Input telemetry:
```json
{
  "device_id": "00:0f:00:70:91:0a",
  "ts": 1696694400,
  "data": {
    "temp": 72.5,
    "humidity": 45.2,
    "co": 0.0024,
    "smoke": 0.015,
    "lpg": 0.008,
    "light": true,
    "motion": false
  }
}
```

LLM Analysis Output:
```
The sensor readings indicate normal environmental conditions. 
Temperature is comfortable at 72.5°F with moderate humidity of 45.2%. 
CO levels are within safe limits at 0.0024 ppm. 
Smoke and LPG levels are minimal and pose no immediate concerns. 
The area is well-lit with no motion detected, suggesting an unoccupied space 
in good condition.
```

## Future Enhancements

- [ ] Model quantization (4-bit, 8-bit) for faster inference
- [ ] Batch processing of multiple telemetry messages
- [ ] Model caching and sharing across devices
- [ ] Real-time metrics dashboard
- [ ] Automated model comparison reports
- [ ] Anomaly detection using LLM analysis
- [ ] Custom prompts via configuration

## References

- [Hugging Face Transformers](https://huggingface.co/docs/transformers)
- [Microsoft Phi-3](https://huggingface.co/microsoft/Phi-3.5-mini-instruct)
- [Edge AI Best Practices](https://developer.nvidia.com/embedded/learn/tutorials)
