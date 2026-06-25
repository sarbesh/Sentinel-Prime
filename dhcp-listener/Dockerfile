FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for packet capture
RUN apt-get update && apt-get install -y \
    tcpdump \
    libpcap-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY dhcp_listener.py .

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash appuser
USER appuser

# Run the DHCP listener
CMD ["python", "dhcp_listener.py"]