# Dockerfile for Raspberry Pi 3 simulation
FROM arm32v7/debian:bullseye-slim

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV DEVICE_NAME=edge-device

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
COPY config/ /etc/edge-device/ 2>/dev/null || true

# Create a startup script
RUN echo '#!/bin/bash\n\
echo "Starting Edge Device: $DEVICE_NAME"\n\
echo "Device ID: $DEVICE_ID"\n\
echo "Configuration loaded from: /etc/edge-device/"\n\
echo "Device is running and ready..."\n\
# Keep container running\n\
tail -f /dev/null\n\
' > /usr/local/bin/start-device.sh && chmod +x /usr/local/bin/start-device.sh

# Set working directory
WORKDIR /app

# Default command
CMD ["/usr/local/bin/start-device.sh"]
