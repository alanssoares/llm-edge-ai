# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added - LLM Inference Features (2025-10-07)
- **LLM Inference Engine** (`src/llm_inference.py`)
  - Support for any Hugging Face Transformers causal language model
  - Default model: Phi-3.5-mini-instruct
  - Configurable via environment variables
  - Automatic GPU/CPU detection and optimization
  - Thread-safe CPU monitoring during inference
  - Energy consumption estimation based on CPU usage and time
  - Comprehensive metrics collection per inference
  - JSON metrics export with summary statistics
  
- **Enhanced Device Simulator** (`src/device_simulator.py`)
  - Integrated LLM inference capabilities
  - Configurable inference intervals
  - New MQTT topics for analysis and metrics
  - Automatic metrics persistence
  - Graceful degradation on LLM errors
  
- **Enhanced Compose Generator** (`src/generate_compose.py`)
  - `--enable-llm` flag for LLM inference
  - `--llm-model` option to specify model
  - `--llm-devices` to enable on specific devices
  - Automatic metrics volume mapping
  - LLM environment variable injection
  
- **Metrics Analysis Tool** (`scripts/analyze_metrics.py`)
  - Load and parse JSON metrics files
  - Summary statistics display
  - Model comparison functionality
  - CSV export for spreadsheet analysis
  - Best performer identification
  
- **Comprehensive Documentation**
  - `docs/LLM_INFERENCE.md` - Complete LLM guide
  - `docs/QUICKSTART_LLM.md` - 5-minute quick start
  - `docs/EXAMPLE_MODEL_COMPARISON.md` - Example configurations
  - `docs/IMPLEMENTATION_SUMMARY.md` - Technical implementation details
  - `metrics/README.md` - Metrics directory guide
  - Updated main `README.md` with LLM features
  
- **Dependencies**
  - transformers>=4.35.0 - Hugging Face models
  - torch>=2.0.0 - PyTorch for inference
  - accelerate>=0.24.0 - Model loading optimizations
  - psutil>=5.9.0 - System metrics collection
  - py-cpuinfo>=9.0.0 - CPU information

### Changed
- Device simulator now supports optional LLM inference
- Docker compose generation includes LLM configuration options
- MQTT topics expanded to include analysis and metrics
- `.env.example` updated with LLM configuration options
- README updated with LLM quick start and features

### Performance Metrics Collected
- **Inference Time** - Milliseconds per inference
- **Memory Usage** - RAM consumption in MB
- **CPU Utilization** - Average percentage during inference
- **Energy Consumption** - Estimated in millijoules
- **Summary Statistics** - Min, max, average for all metrics

### Supported Models
- microsoft/Phi-3.5-mini-instruct (default)
- TinyLlama/TinyLlama-1.1B-Chat-v1.0
- microsoft/Phi-3-mini-4k-instruct
- google/gemma-2b-it
- stabilityai/stablelm-2-1_6b
- Any Hugging Face causal language model

## [Previous Releases]

### Added
- Restructured project with `src/` directory
- Added comprehensive test suite with pytest
- Added logging support with configurable levels
- Added type hints throughout codebase
- Added `pyproject.toml` for modern Python packaging
- Added development dependencies in `requirements-dev.txt`
- Added `.env.example` for environment variable documentation
- Added `.gitignore` and `.dockerignore` files
- Added `CONTRIBUTING.md` with contribution guidelines
- Added `CHANGELOG.md` to track changes
- Added proper Python package structure with `__init__.py`

### Changed
- Improved code organization with src/tests structure
- Enhanced error handling and logging
- Updated documentation to reflect new structure
- Migrated from print statements to proper logging

### Removed
- Removed Makefile in favor of direct Python/Docker commands

## [0.1.0] - 2025-10-05

### Added
- Initial project structure
- IoT device simulator with MQTT support
- MQTT consumer for telemetry monitoring
- Docker Compose generator for scalable device simulation
- Support for 10 to 1000+ simulated devices
- Real dataset-based telemetry simulation
- Docker containerization
- Comprehensive README documentation

[Unreleased]: https://github.com/alanssoares/llm-edge-ai/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/alanssoares/llm-edge-ai/releases/tag/v0.1.0
