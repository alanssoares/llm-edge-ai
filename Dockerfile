# syntax=docker/dockerfile:1.3
# Dockerfile for Raspberry Pi 3 simulation with MQTT telemetry
FROM --platform=linux/arm/v7 arm32v7/debian:bullseye-slim

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV DEVICE_NAME=edge-device
ENV MQTT_BROKER=mqtt-broker
ENV MQTT_PORT=1883

# Install basic utilities and tools commonly found on Raspberry Pi
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    nano \
    vim \
    python3 \
    python3-pip \
    i2c-tools \
    && rm -rf /var/lib/apt/lists/*

# Create a directory for device configuration
RUN mkdir -p /etc/edge-device

# Copy device configuration if exists
COPY config/ /etc/edge-device/

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy the device simulator script
COPY device_simulator.py .

# Copy the dataset
COPY dataset/ ./dataset/

# Make the simulator script executable
RUN chmod +x device_simulator.py

# Default command - run the device simulator
CMD ["python3", "device_simulator.py"]
