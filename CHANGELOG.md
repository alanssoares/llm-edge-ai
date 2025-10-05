# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
