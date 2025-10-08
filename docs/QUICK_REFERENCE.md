# LLM Edge AI - Quick Reference

Quick reference for common commands and configurations.

## Generate Docker Compose

```bash
# Basic (no LLM)
python src/generate_compose.py --devices 5

# With LLM on all devices
python src/generate_compose.py --devices 5 --enable-llm

# With LLM on specific devices
python src/generate_compose.py --devices 5 --enable-llm --llm-devices "1,3,5"

# Different model
python src/generate_compose.py --devices 3 --enable-llm --llm-model "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
```

## Docker Commands

```bash
# Start system
docker compose up --build

# Start in background
docker compose up -d --build

# View logs
docker logs -f edge-device-01

# View all logs
docker compose logs -f

# Stop system
docker compose down

# View resource usage
docker stats

# Restart device
docker compose restart edge-device-01
```

## MQTT Monitoring

```bash
# All topics
docker exec -it mqtt-broker mosquitto_sub -t "#" -v

# Telemetry only
docker exec -it mqtt-broker mosquitto_sub -t "iot/telemetry/#" -v

# Analysis results (LLM)
docker exec -it mqtt-broker mosquitto_sub -t "iot/analysis/#" -v

# Metrics (LLM)
docker exec -it mqtt-broker mosquitto_sub -t "iot/metrics/#" -v
```

## Metrics Analysis

```bash
# View summary
python scripts/analyze_metrics.py

# Compare models
python scripts/analyze_metrics.py --compare

# Export to CSV
python scripts/analyze_metrics.py --export-csv results.csv

# Specific device
python scripts/analyze_metrics.py --device edge-device-01

# Custom metrics directory
python scripts/analyze_metrics.py --metrics-dir results --compare
```

## View Metrics Files

```bash
# List metrics
ls -lh metrics/edge-device-01/

# View latest
cat metrics/edge-device-01/*.json | python -m json.tool

# View summary only
cat metrics/edge-device-01/*.json | python -m json.tool | grep -A 20 '"summary"'
```

## Model Comparison Workflow

```bash
# Test Model A
python src/generate_compose.py --devices 1 --enable-llm --llm-model "microsoft/Phi-3.5-mini-instruct"
docker compose up --build
# Wait 30 minutes
docker compose down
mkdir -p results/phi35 && cp -r metrics/edge-device-01/* results/phi35/

# Test Model B
python src/generate_compose.py --devices 1 --enable-llm --llm-model "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
docker compose up --build
# Wait 30 minutes
docker compose down
mkdir -p results/tinyllama && cp -r metrics/edge-device-01/* results/tinyllama/

# Compare
python scripts/analyze_metrics.py --metrics-dir results --compare --export-csv comparison.csv
```

## Environment Variables

```bash
# Set in docker-compose.yml under environment:
- ENABLE_LLM=true
- LLM_MODEL_NAME=microsoft/Phi-3.5-mini-instruct
- LLM_INFERENCE_INTERVAL=5
- LLM_MAX_LENGTH=512
- LLM_TEMPERATURE=0.7
```

## Recommended Models

```yaml
# Balanced (default)
LLM_MODEL_NAME=microsoft/Phi-3.5-mini-instruct

# Lightweight
LLM_MODEL_NAME=TinyLlama/TinyLlama-1.1B-Chat-v1.0

# Compact
LLM_MODEL_NAME=microsoft/Phi-3-mini-4k-instruct

# Google
LLM_MODEL_NAME=google/gemma-2b-it
```

## Performance Tuning

```yaml
# Resource-constrained
- ENABLE_LLM=true
- LLM_MODEL_NAME=TinyLlama/TinyLlama-1.1B-Chat-v1.0
- LLM_INFERENCE_INTERVAL=10
- LLM_MAX_LENGTH=256
- LLM_TEMPERATURE=0.3

# High-performance
- ENABLE_LLM=true
- LLM_MODEL_NAME=microsoft/Phi-3.5-mini-instruct
- LLM_INFERENCE_INTERVAL=3
- LLM_MAX_LENGTH=1024
- LLM_TEMPERATURE=0.7
```

## Memory Limits

```yaml
# Add to service in docker-compose.yml
edge-device-01:
  mem_limit: 4g
  memswap_limit: 6g
```

## Troubleshooting

```bash
# Check logs for errors
docker logs edge-device-01 2>&1 | tail -100

# View resource usage
docker stats edge-device-01

# Test MQTT connection
docker exec -it mqtt-broker mosquitto_sub -t "#" -c 10

# Clear metrics
rm -rf metrics/edge-device-*/

# Pre-download model
pip install transformers torch
python -c "from transformers import AutoModelForCausalLM; AutoModelForCausalLM.from_pretrained('microsoft/Phi-3.5-mini-instruct')"
```

## File Locations

```
metrics/              # LLM metrics (generated)
config/              # Configuration files
dataset/             # IoT telemetry data
docs/                # Documentation
src/                 # Source code
scripts/             # Utility scripts
docker-compose.yml   # Generated compose file
```

## Documentation

- **Quick Start**: `docs/QUICKSTART_LLM.md`
- **Full Guide**: `docs/LLM_INFERENCE.md`
- **Examples**: `docs/EXAMPLE_MODEL_COMPARISON.md`
- **Implementation**: `docs/IMPLEMENTATION_SUMMARY.md`
- **Main README**: `README.md`

## Common Issues

| Issue | Solution |
|-------|----------|
| Out of memory | Use smaller model or increase mem_limit |
| Slow inference | Reduce LLM_MAX_LENGTH or increase interval |
| Model won't download | Pre-download on host, mount cache |
| Container crashes | Check logs, increase memory |
| No metrics | Verify ENABLE_LLM=true and device is running |

## Quick Test

```bash
# Minimal test setup
python src/generate_compose.py --devices 1 --enable-llm --llm-devices "1"
docker compose up --build

# In another terminal
docker logs -f edge-device-01 | grep "Inference"

# Wait for a few inferences, then check
cat metrics/edge-device-01/*.json | python -m json.tool | head -50
```

## Performance Expectations

| Model | Memory | Inference Time | Energy/Inference |
|-------|--------|----------------|------------------|
| Phi-3.5 | 3-5GB | 1.5-3s | 25-40 mJ |
| TinyLlama | 1-2GB | 0.5-1.5s | 8-20 mJ |
| Phi-3-mini | 2-3GB | 1-2s | 15-30 mJ |

## Next Steps

1. Start with Quick Start: `docs/QUICKSTART_LLM.md`
2. Test with TinyLlama for fast results
3. Compare models for your hardware
4. Analyze metrics with provided tools
5. Optimize based on your requirements
