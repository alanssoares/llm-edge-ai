# Tests

This directory contains unit tests for the LLM Edge AI project.

## Running Tests

### Run All Tests

```bash
pytest
```

### Run Specific Test File

```bash
pytest tests/test_simulator.py
pytest tests/test_consumer.py
pytest tests/test_generate_compose.py
```

### Run with Coverage

```bash
pytest --cov=src --cov-report=html
```

Coverage report will be generated in `htmlcov/index.html`.

### Run Specific Test

```bash
pytest tests/test_simulator.py::TestIoTDeviceSimulator::test_device_initialization
```

### Run with Verbose Output

```bash
pytest -v
```

### Run with Print Statements

```bash
pytest -s
```

## Test Structure

```
tests/
├── __init__.py
├── test_simulator.py         # Tests for IoT device simulator
├── test_consumer.py          # Tests for MQTT consumer
└── test_generate_compose.py  # Tests for compose generator
```

## Writing Tests

### Example Test

```python
import pytest
from src.device_simulator import IoTDeviceSimulator

def test_device_initialization():
    """Test device initialization"""
    device = IoTDeviceSimulator(
        device_id="test-id",
        device_name="test-device"
    )
    
    assert device.device_id == "test-id"
    assert device.device_name == "test-device"
```

### Using Fixtures

```python
@pytest.fixture
def mock_device():
    """Fixture for creating a test device"""
    return IoTDeviceSimulator(
        device_id="test-id",
        device_name="test-device"
    )

def test_with_fixture(mock_device):
    """Test using fixture"""
    assert mock_device.device_id == "test-id"
```

### Mocking

```python
from unittest.mock import Mock, patch

@patch('device_simulator.mqtt.Client')
def test_mqtt_connection(mock_mqtt_client):
    """Test MQTT connection with mocking"""
    device = IoTDeviceSimulator("test-id", "test-device")
    # Test implementation
```

## Test Coverage Goals

- **Minimum**: 70% coverage
- **Target**: 85% coverage
- **Ideal**: 95% coverage

## Continuous Integration

Tests are automatically run on:
- Pull requests
- Commits to main branch
- Release tags

## Troubleshooting

### Import Errors

If you get import errors, make sure the `src` directory is in your Python path:

```python
import sys
from pathlib import Path
src_path = Path(__file__).parent.parent / 'src'
sys.path.insert(0, str(src_path))
```

### Missing Dependencies

Install development dependencies:

```bash
pip install -r requirements-dev.txt
```

### Async Tests

For async code, use pytest-asyncio:

```python
import pytest

@pytest.mark.asyncio
async def test_async_function():
    result = await async_function()
    assert result == expected
```
