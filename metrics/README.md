# Metrics Directory

This directory stores LLM inference metrics collected from edge devices.

## Structure

```
metrics/
├── edge-device-01/
│   ├── inference_metrics_00:0f:00:70:91:0a_20251007_103015.json
│   ├── inference_metrics_00:0f:00:70:91:0a_20251007_110530.json
│   └── loading_metrics.json
├── edge-device-02/
│   └── inference_metrics_1c:bf:ce:15:ec:4d_20251007_103020.json
└── ...
```

## Metric Files

### Inference Metrics
Files named `inference_metrics_*.json` contain:
- Summary statistics (min, max, avg)
- Detailed per-inference metrics
- Timestamps and device information

### Loading Metrics
Files named `loading_metrics.json` contain:
- Model loading time
- Memory increase during model load
- Compute device information

## Analyzing Metrics

Use the provided analysis tool:

```bash
# View summary of all metrics
python scripts/analyze_metrics.py

# Compare models
python scripts/analyze_metrics.py --compare

# Export to CSV
python scripts/analyze_metrics.py --export-csv results.csv

# Analyze specific device
python scripts/analyze_metrics.py --device edge-device-01
```

## Automatic Collection

Metrics are automatically:
- Collected during each LLM inference
- Saved every 50 messages (10 inferences × 5 interval)
- Saved when the device shuts down
- Published to MQTT topic `iot/metrics/{device_id}`

## Persistence

Metrics are stored in Docker volumes mapped to this directory:

```yaml
volumes:
  - ./metrics/edge-device-01:/app/metrics
```

This ensures metrics survive container restarts.

## File Format

Example metrics file structure:

```json
{
  "summary": {
    "device_id": "00:0f:00:70:91:0a",
    "model_name": "microsoft/Phi-3.5-mini-instruct",
    "total_inferences": 10,
    "inference_time_ms": {
      "min": 1234.56,
      "max": 2345.67,
      "avg": 1789.12
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
  },
  "detailed_metrics": [
    {
      "timestamp": "2025-10-07T10:30:15.123456",
      "device_id": "00:0f:00:70:91:0a",
      "model_name": "microsoft/Phi-3.5-mini-instruct",
      "inference_time_ms": 1234.56,
      "memory_used_mb": 45.67,
      "cpu_percent_avg": 78.5,
      "energy_consumed_mj": 18.75,
      "compute_device": "cpu"
    }
  ]
}
```

## Best Practices

1. **Backup**: Regularly backup this directory for long-term studies
2. **Cleanup**: Remove old metrics files to save disk space
3. **Organization**: Use subdirectories for different experiments
4. **Comparison**: Keep metrics from different models in separate runs

## Disk Space

Typical file sizes:
- Per-inference entry: ~500 bytes
- 100 inferences: ~50 KB
- 1000 inferences: ~500 KB
- Daily metrics (per device): ~1-5 MB

For 10 devices running 24 hours: ~10-50 MB/day

## Cleaning Up

```bash
# Remove all metrics
rm -rf metrics/edge-device-*/

# Remove metrics older than 7 days
find metrics/ -name "*.json" -mtime +7 -delete

# Archive old metrics
tar -czf metrics_archive_$(date +%Y%m%d).tar.gz metrics/
```

## Integration

Metrics can be:
- Exported to CSV for Excel/spreadsheet analysis
- Imported into databases for long-term storage
- Visualized with custom dashboards
- Analyzed with pandas/numpy for statistical studies
- Compared across different hardware platforms
