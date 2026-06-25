# SENTINEL PRIME Setup and Running Guide

This guide provides step-by-step instructions for setting up and running the Sentinel Prime home network security system on any home network.

## Table of Contents
1. [System Requirements](#system-requirements)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Running the System](#running-the-system)
5. [Verifying the Installation](#verifying-the-installation)
6. [Integrating with AI Agents (MCP)](#integrating-with-ai-agents-mcp)
7. [Troubleshooting](#troubleshooting)
8. [Production Considerations](#production-considerations)

## System Requirements

### Hardware Requirements
- Minimum: 2GB RAM, 2-core CPU, 20GB storage
- Recommended: 4GB+ RAM, 4-core CPU, 50GB+ storage
- Network interface capable of promiscuous mode (for packet capture)

### Software Requirements
- Docker Engine 20.10+
- Docker Compose v2.0+
- Git (for cloning the repository)
- curl or similar tool for testing endpoints

### Supported Operating Systems
- Linux (Ubuntu 20.04+, Debian 11+, CentOS 8+)
- macOS (Docker Desktop)
- Windows 10/11 (Docker Desktop or WSL2)

## Installation

### Step 1: Clone the Repository
```bash
git clone <repository-url>
cd sentinel-prime
```

### Step 2: Verify Docker Installation
```bash
docker --version
docker compose version
```

Both commands should return version information without errors.

### Step 3: Review Environment Variables (Optional)
The system uses several environment variables for configuration. You can review and modify them in:
- `.env` file (root directory)
- `backend/docker-compose.override.yml` (for backend-specific overrides)

Key environment variables:
- `OTX_API_KEY`: For AlienVault OTX threat intelligence (optional)
- `ABUSECH_API_KEY`: For Abuse.ch threat intelligence feeds (optional)
- `UI_VERSION_SHA`: For frontend versioning (auto-generated during build)
- `MCP_API_KEY`: For MCP server authentication (default: "sentinel-prime-mcp-default")

## Configuration

### Threat Intelligence Feeds (Optional)
To enable threat intelligence feeds, obtain API keys from:
1. [AlienVault OTX](https://otx.alienvault.com/) - Sign up for free API key
2. [Abuse.ch](https://abuse.ch/) - Register for API keys (some feeds free, some paid)

Add these keys to your `.env` file:
```
OTX_API_KEY=your_otx_api_key_here
ABUSECH_API_KEY=your_abusech_api_key_here
```

### MCP Authentication (Optional)
By default, the MCP server uses a simple API key for authentication. To change it:
1. Generate a secure random string (e.g., `openssl rand -hex 32`)
2. Update the `MCP_API_KEY` in your `.env` file
3. The same key will need to be used by any AI agents connecting to the MCP server

### Network Scanning Configuration
The system is configured to scan common home network ranges by default. To customize:
- Modify the default scan targets in backend API or through MCP tasks
- Adjust scan types and timing as needed for your network

## Running the System

### Using Docker Compose (Recommended)
```bash
# Start all services in detached mode
docker compose up -d

# View logs to verify startup
docker compose logs -f

# To stop all services
docker compose down

# To stop and remove all volumes (including database)
docker compose down -v
```

### Running Backend Only (For Development)
```bash
cd backend
# Install Python dependencies
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Run the backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Running Frontend Only (For Development)
```bash
cd web-ui
# Install Node.js dependencies
npm install

# Start development server
npm run dev
```

## Verifying the Installation

### Check Service Status
```bash
docker compose ps
```
Should show all services as "healthy" or "running".

### Test Basic Endpoints
```bash
# Backend health check
curl -s http://localhost:8000/health
# Expected: {"status":"ok"}

# Backend root endpoint
curl -s http://localhost:8000/
# Expected: {"msg":"Sentinel Prime Backend is running"}

# MCP health check
curl -s http://localhost:8001/health
# Expected: {"status":"ok","service":"sentinel-prime-mcp"}

# MCP agent info
curl -s http://localhost:8001/mcp/agent
# Should return agent information including capabilities
```

### Verify Database Initialization
```bash
# Check if database file was created (for SQLite fallback)
ls -la backend/sentinel_prime.db

# Or check PostgreSQL if using Docker
docker compose exec vector-db psql -U postgres -d vectordb -c "\dt"
```

## Integrating with AI Agents (MCP)

The MCP (Model Context Protocol) server enables AI agents to interact with Sentinel Prime programmatically.

### MCP Endpoints
All MCP endpoints are available at `http://localhost:8001` (or your configured host):

#### 1. Agent Information
```bash
curl -s http://localhost:8001/mcp/agent
```
Returns information about the MCP agent including name, version, and capabilities.

#### 2. Health Checks
```bash
# Basic health
curl -s http://localhost:8001/health

# MCP-specific health
curl -s http://localhost:8001/mcp/health
```

#### 3. Task Submission
AI agents can submit tasks for execution:
```bash
curl -X POST http://localhost:8001/mcp/task \
  -H "Content-Type: application/json" \
  -H "x-api-key: sentinel-prime-mcp-default" \
  -d '{
    "task_id": "scan-home-network-001",
    "description": "Scan home network for vulnerabilities",
    "parameters": {
      "target": "192.168.1.0/24",
      "scan_type": "quick"
    }
  }'
```

#### 4. Result Retrieval
Check status and results of submitted tasks:
```bash
# Get specific task
curl -s http://localhost:8001/mcp/task/scan-home-network-001

# List all tasks (optional filtering)
curl -s http://localhost:8001/mcp/task?limit=10
```

### Available MCP Tools

#### Network Scanning
- `list_devices` - Get all discovered network devices
- `get_device` - Get details of a specific device by ID
- `get_device_by_ip` - Get device details by IP address
- `get_device_by_mac` - Get device details by MAC address
- `create_device` - Manually add a device to monitoring
- `update_device` - Update device information
- `delete_device` - Remove device from monitoring
- `trigger_scan` - Initiate a network security scan
- `get_scan` - Get details of a specific scan
- `list_scans` - List all scans with optional filtering

#### Security Monitoring
- `get_alerts` - Get security alerts (filter by acknowledged status, severity)
- `get_alert` - Get specific alert by ID
- `create_alert` - Create a new security alert
- `acknowledge_alert` - Acknowledge a security alert

#### Honeypot Events
- `get_honeypot_events` - Get honeypot detection events (filter by type, limit)

#### Vulnerability Management
- `list_vulnerabilities` - List vulnerabilities (filter by device ID, severity)
- `get_vulnerability` - Get specific vulnerability details
- `acknowledge_vulnerability` - Acknowledge a vulnerability

#### System Management
- `get_settings` - Get system settings (optional key filter)
- `update_settings` - Update system settings
- `get_network_status` - Get overall network security status summary

### Example AI Agent Workflow

Here's an example of how an AI agent might interact with Sentinel Prime:

1. **Discover Capabilities**
   ```python
   agent_info = mcp_client.get_agent_info()
   tools = mcp_client.list_tools()
   ```

2. **Perform Network Discovery**
   ```python
   devices = mcp_client.list_devices(status="online")
   ```

3. **Initiate Security Scan**
   ```python
   scan_task = mcp_client.submit_task(
       task_id=f"scan-{int(time.time())}",
       description="Weekly network security scan",
       parameters={
           "target": "192.168.1.0/24",
           "scan_type": "deep",
           "ports": "1-1000"
       }
   )
   ```

4. **Monitor Scan Progress**
   ```python
   while True:
       status = mcp_client.get_task_status(scan_task.task_id)
       if status in ["completed", "failed"]:
           break
       time.sleep(5)
   ```

5. **Review Results and Take Action**
   ```python
   results = mcp_client.get_task_result(scan_task.task_id)
   vulnerabilities = mcp_client.list_vulnerabilities(scan_id=results.scan_id)
   
   if vulnerabilities.critical_count > 0:
       # Create high-priority alert
       mcp_client.create_alert({
           "source": "mcp_agent",
           "severity": "critical",
           "title": "Critical Vulnerabilities Detected",
           "description": f"Found {vulnerabilities.critical_count} critical vulnerabilities"
       })
   ```

## Troubleshooting

### Common Issues and Solutions

#### 1. Services Not Starting
**Symptom**: `docker compose ps` shows services as "exited" or "unhealthy"
**Solution**:
```bash
# Check logs for specific service
docker compose logs backend
docker compose logs scanner
docker compose logs vector-db

# Common fixes:
# - Insufficient resources: Increase RAM/CPU allocation to Docker
# - Port conflicts: Ensure ports 8000, 8001, 5432 are free
# - Volume permissions: Check file permissions on mounted directories
```

#### 2. Database Connection Issues
**Symptom**: Backend logs show database connection errors
**Solution**:
```bash
# Verify database service is running
docker compose ps vector-db

# Check database logs
docker compose logs vector-db

# If using SQLite fallback, check file permissions
ls -la backend/sentinel_prime.db
```

#### 3. Scanner Not Working
**Symptom**: Scan requests fail or return errors
**Solution**:
```bash
# Check scanner logs
docker compose logs scanner

# Verify nmap is available in scanner container
docker compose exec scanner which nmap

# For development/testing, mock mode is available when nmap is not present
```

#### 4. MCP Authentication Issues
**Symptom**: MCP requests return 401 Unauthorized
**Solution**:
```bash
# Verify you're sending the correct API key
# Default key is: sentinel-prime-mcp-default
# Check .env file for MCP_API_KEY value

# Example curl with correct header:
curl -H "x-api-key: sentinel-prime-mcp-default" http://localhost:8001/mcp/agent
```

### Diagnostic Commands
```bash
# Check Docker container status
docker compose ps

# View logs for all services
docker compose logs --tail=50

# Check resource usage
docker compose stats

# Verify network connectivity
docker compose network ls

# Check volume mounts
docker compose inspect backend | grep -A5 -B5 "Mounts"
```

## Production Considerations

### Security Recommendations
1. **Change Default Passwords/Keys**
   - Update `MCP_API_KEY` in `.env` file
   - Consider adding authentication to other endpoints if exposed externally

2. **Network Segmentation**
   - Consider running Sentinel Prime in a dedicated VLAN or subnet
   - Ensure the monitoring port has visibility into network traffic

3. **Regular Updates**
   ```bash
   # Pull latest image updates
   docker compose pull
   
   # Recreate containers with updated images
   docker compose up -d --build
   ```

4. **Backup Strategy**
   - Regularly backup the PostgreSQL database:
     ```bash
     docker compose exec vector-db pg_dump -U postgres vectordb > backup.sql
     ```
   - Or for SQLite fallback:
     ```bash
     cp backend/sentinel_prime.db backups/sentinel_prime_$(date +%Y%m%d).db
     ```

5. **Monitoring and Logging**
   - Consider setting up log rotation for container logs
   - Monitor container resource usage over time
   - Set up alerts for service failures

### Performance Tuning
1. **Adjust Scan Frequency**
   - Modify cron jobs or MCP task scheduling based on network size
   - Larger networks may need less frequent deep scans

2. **Database Optimization**
   - Monitor database size and performance
   - Consider archiving old scan data and alerts
   - vacuum analyze PostgreSQL periodically

3. **Resource Allocation**
   - Adjust Docker resource limits in `docker-compose.yml` if needed:
     ```yaml
     deploy:
       resources:
         limits:
           cpus: "2.0"
           memory: 2G
         reservations:
           cpus: "500m"
           memory: 512M
     ```

## Updating the System

### To Get Latest Changes
```bash
# Pull latest code
git pull origin main

# Update Python dependencies (if needed)
cd backend
pip install -r requirements.txt

# Update frontend dependencies (if needed)
cd ../web-ui
npm install

# Rebuild and restart containers
docker compose up -d --build
```

### Migrating Data
When updating between major versions, check the CHANGELOG.md for migration instructions.
Typically, data migrations are handled automatically on startup, but always backup first.

## Support and Community

For issues, questions, or contributions:
1. Check the existing documentation in the `docs/` directory
2. Review the `Troubleshooting` section above
3. Look through the `TODO.md` for known issues and planned features
4. Consider opening an issue in the repository if you encounter a bug
5. Contribute fixes or features via pull requests

## License
SENTINEL PRIME is released under the [LICENSE](LICENSE) file in the repository root.

---
*Last updated: Thursday 18 June 2026 08:33:41 AM IST*
*Version: 0.1.0*
