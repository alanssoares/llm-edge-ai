# syntax=docker/dockerfile:1.4
# Fast Single-Stage Dockerfile for edge device simulation with MQTT telemetry

FROM python:3.11-slim

# Set environment variables for optimization
ENV DEBIAN_FRONTEND=noninteractive
ENV DEVICE_NAME=edge-device
ENV MQTT_BROKER=mqtt-broker
ENV MQTT_PORT=1883
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# Install runtime dependencies in one layer
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Create directories and user in one layer
RUN mkdir -p /app /etc/edge-device /app/dataset \
    && groupadd -r edgeuser \
    && useradd -r -g edgeuser -s /bin/false edgeuser \
    && chown -R edgeuser:edgeuser /app

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies (using pre-compiled ARM wheels)
COPY requirements.txt .
RUN pip3 install --no-cache-dir --upgrade pip \
    && pip3 install --no-cache-dir -r requirements.txt \
    && rm requirements.txt

# Copy application files
COPY device_simulator.py .
COPY config/ /etc/edge-device/

# Switch to non-root user
USER edgeuser

# Add minimal health check
HEALTHCHECK --interval=60s --timeout=5s --start-period=10s --retries=2 \
    CMD python3 -c "import paho.mqtt.client; exit(0)" || exit 1

# Note: Large dataset (61MB) will be mounted as volume for better performance
# This reduces image size and build time while maintaining functionality

# Default command - run the device simulator
CMD ["python3", "device_simulator.py"]
