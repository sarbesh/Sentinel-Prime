# DHCP Listener Implementation for SENTINEL PRIME

## Overview
This document describes the implementation of a DHCP listener container that detects new devices on the network via DHCP requests and triggers network scans via the backend API. The implementation complements the existing ARP-based passive monitoring by providing active detection of devices as they join the network.

## Components Created

### 1. DHCP Listener Application (`dhcp-listener/dhcp_listener.py`)
A Python script that:
- Listens for DHCP packets on UDP ports 67 (server) and 68 (client)
- Extracts MAC address, IP address, and hostname from DHCP options
- Prevents duplicate processing using a simple MAC address cache
- Sends new device information to the backend API via `/devices/` endpoint
- Triggers a quick network scan for the new device via `/scans/network` endpoint
- Uses Scapy for packet capture and parsing

### 2. Dockerfile (`dhcp-listener/Dockerfile`)
- Based on Python 3.11-slim image
- Installs necessary system dependencies (tcpdump, libpcap-dev)
- Copies application code and installs Python requirements (scapy, requests)
- Runs as non-root user for security
- Executes the DHCP listener script

### 3. Requirements (`dhcp-listener/requirements.txt`)
- scapy>=2.4.5: For packet capture and DHCP parsing
- requests>=2.25.1: For HTTP communication with backend API

### 4. Docker Compose Updates (`docker-compose.yml`)
Added new service:
```yaml
  dhcp-listener:
    build:
      context: ./dhcp-listener
      dockerfile: Dockerfile
    container_name: sentinel-prime-dhcp-listener
    network_mode: host  # Required for packet capture
    environment:
      - BACKEND_URL=http://backend:8000
      - INTERFACE=eth0
    restart: unless-stopped
    depends_on:
      backend:
        condition: service_healthy
    cap_add:
      - NET_RAW
      - NET_ADMIN
```

## How It Works

### Packet Capture
The listener uses Scapy's `sniff()` function with a BPF filter:
```
udp and (port 67 or port 68)
```
This captures both DHCP client requests (port 68) and server responses (port 67).

### DHCP Packet Processing
When a DHCP packet is received:
1. Extract MAC address from Ethernet layer
2. Parse DHCP options to get:
   - Hostname (option 12)
   - Requested IP address (option 50)
   - Fallback to IP layer's yiaddr field if needed
3. Check against MAC cache to prevent immediate duplicates
4. Send device data to backend API:
   ```json
   {
     "mac_address": "AA:BB:CC:DD:EE:FF",
     "ip_address": "192.168.1.100",
     "hostname": "device-hostname",
     "status": "online",
     "type": "unknown"
   }
   ```
5. Trigger network scan:
   ```json
   {
     "target": "192.168.1.100",
     "scan_type": "quick",
     "ports": ""
   }
   ```

### Integration with Existing Systems
- **Backend Dependency**: Waits for backend to be healthy before starting
- **Network Mode**: Uses `host` network mode for direct interface access
- **Capabilities**: Requires `NET_RAW` and `NET_ADMIN` for packet capture
- **Duplicate Prevention**: Simple in-memory MAC cache (resets on container restart)
- **Scan Type**: Uses quick scan for fast initial assessment

## Configuration Options
- `BACKEND_URL`: URL of the SENTINEL PRIME backend API (default: http://backend:8000)
- `INTERFACE`: Network interface to listen on (default: eth0)

## Security Considerations
- Runs as non-root user in container
- Only necessary Linux capabilities added (NET_RAW, NET_ADMIN)
- No persistent storage of MAC cache (privacy-preserving)
- Limited to local network interface

## Future Enhancements
1. Persistent MAC cache with TTL to survive container restarts
2. Integration with ARP monitor for correlated detection
3. Support for DHCPv6 (currently IPv4 only)
4. Vendor classification from MAC OUI
5. Configurable scan types based on device type
6. Integration with alerting for suspicious DHCP patterns

## Verification
The implementation has been designed to:
1. Work with existing SENTINEL PRIME backend API
2. Integrate seamlessly with docker-compose setup
3. Require minimal configuration
4. Provide immediate value upon device connection
5. Not interfere with existing ARP-based monitoring