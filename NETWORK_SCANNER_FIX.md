# Network Scanner Issue - RESOLVED

## Problem
- Devices showing as offline despite being online
- Router at `192.168.0.1` not detected
- Scanner was running in mock mode and generating fake results

## Root Causes Identified

### 1. Network Mismatch
- **Issue**: Old scans were on `192.168.1.x` network (from March 2026)
- **Current Network**: `192.168.0.x` with router at `192.168.0.1`
- **Solution**: Triggered new scan on correct network range

### 2. Scanner Container Network Isolation
- **Issue**: Scanner service running in Docker bridge network couldn't reach host's local network
- **Impact**: nmap scans returned no results, fell back to mock data generation
- **Solution**: Changed scanner to use `network_mode: host` for direct network access

### 3. Backend Missing nmap
- **Issue**: Backend container didn't have nmap installed
- **Impact**: API-triggered scans (`POST /scans/network`) failed or returned mock data
- **Solution**: Updated backend Dockerfile to install nmap + python-nmap

### 4. Scanner Volume Mount Conflict
- **Issue**: Volume mount `./scanner:/app` was overriding container files
- **Solution**: Removed unnecessary volume mount from scanner service

## Changes Made

### Backend Dockerfile (`backend/Dockerfile`)
```dockerfile
# Added nmap installation
RUN apt-get update && apt-get install -y libpcap-dev nmap

# Added python-nmap to pip install
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt python-nmap
```

### Docker Compose (`docker-compose.yml`)

#### Backend Service
```yaml
backend:
  network_mode: host  # Added for network scanning
  cap_add:
    - NET_RAW         # Added for nmap permissions
    - NET_ADMIN
  environment:
    - VECTOR_DB_URL=postgresql://postgres:postgres@localhost:5432/vectordb  # Changed to localhost
```

#### Scanner Service
```yaml
scanner:
  network_mode: host  # Changed from bridge network
  cap_add:
    - NET_RAW
    - NET_ADMIN
  environment:
    - API_URL=http://localhost:8000  # Changed from backend:8000
  # Removed volume mount that was conflicting
```

## Verification Results

### Before Fix
- All devices showing as "offline"
- Router `192.168.0.1` not in database
- Scanner returning mock data with fake MAC addresses (e.g., `02:02:02:02:02:02`)

### After Fix
```bash
$ curl POST /scans/network with target "192.168.0.1/24"
Scan 18: Found 3 hosts

192.168.0.1 - MAC: 3C:78:95:E4:BC:AB - Status: online ✓
192.168.0.3 - MAC: D2:E3:49:F3:68:19 - Status: online ✓  
192.168.0.4 - MAC: unknown - Status: online ✓
```

### Current Device Status
```
127.0.0.1 - localhost - online
192.168.0.1 - Router - online ✓ (NEW, correct MAC)
192.168.0.3 - Device - online ✓ (Real MAC)
192.168.1.x devices - offline (correct, old network)
```

## How Network Scanning Works Now

1. **User triggers scan** via Web UI or API: `POST /scans/network`
2. **Backend receives request** and calls `run_scanner()` function
3. **Backend executes** `/scanner/scanner.py` via subprocess (volume-mounted from host)
4. **Scanner imports python-nmap** and runs actual nmap scan on host network
5. **Results returned** to backend with real IPs, MACs, and services
6. **Backend updates database** with scanned devices and their status

## Key Technical Details

### Why Host Network Mode?
- Docker bridge network uses NAT - containers see different network interfaces
- nmap needs to scan the physical network interface (enp7s0, eth0, etc.)
- Host mode gives container direct access to host's network stack
- Required for scanning local network devices like routers, phones, IoT devices

### Why NET_RAW and NET_ADMIN Capabilities?
- nmap uses raw sockets for ping scans and port scanning
- Requires elevated privileges to craft custom network packets
- Standard Docker containers don't have these capabilities by default

### Backend vs Scanner Service
- **Backend**: Runs the API and executes scanner.py via subprocess
- **Scanner Service**: Polls for queued jobs (alternative scanning method)
- Both now have network scanning capabilities
- Primary method: Backend executes scanner directly (synchronous)
- Secondary method: Scanner service polls queue (asynchronous)

## Next Steps (Optional)

1. **Clean old devices**: Remove offline `192.168.1.x` devices from database
2. **Add vulnerability scanning**: Run deeper scans to find services/versions
3. **Scheduled scans**: Set up cron job for periodic network discovery
4. **Device naming**: Add manual device names/hostnames to identified devices
5. **Alert on new devices**: Notify when unknown devices join the network

---

**Status**: RESOLVED ✅  
**Date**: June 22, 2026  
**Services**: All healthy and scanning correctly