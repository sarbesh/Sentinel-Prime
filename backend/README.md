# SENTINEL PRIME Backend

This is the backend for SENTINEL PRIME, a network security monitoring system.

## Features

- FastAPI backend with PostgreSQL and pgvector for storage
- DHCP listener to detect new devices on the network
- Threat intelligence updater that fetches indicators from OTX and Abuse.ch
- Dockerized for easy deployment
- MCP server for AI/LLM agent integration
- Network reconnaissance and IDS/IPS control via MCP tasks

## Services

- `backend`: The FastAPI application
- `db`: PostgreSQL database with pgvector extension

## Setup

1. Copy `.env.example` to `.env` and fill in the required environment variables.
2. Build and start the services:
   ```
   docker-compose up --build
   ```
3. The API will be available at `http://localhost:8000`

## Environment Variables

- `DATABASE_URL`: PostgreSQL connection string (default: `postgresql://user:password@db:5432/sentinel_prime`)
- `OTX_API_KEY`: API key for AlienVault OTX
- `ABUSECH_API_KEY`: API key for Abuse.ch (if required for certain feeds)
- `DHCP_LISTENER_INTERFACE`: Network interface to listen on (default: `eth0`)
- `DHCP_LISTENER_PORT`: Port to listen on for DHCP (default: `67`)
- `THREAT_INTEL_UPDATE_INTERVAL`: Interval in seconds between threat intelligence updates (default: `3600`)

## Modules

### DHCP Listener

Listens for DHCP packets on the specified interface. When a new device is detected (by MAC address), it adds the device to the database and logs the event.

### Threat Intelligence Updater

Periodically fetches threat intelligence data from:
- OTX (AlienVault Open Threat Exchange)
- Abuse.ch (SSLBlacklist, URLHaus, and more feeds can be added)

The fetched indicators are stored in the `threat_intelligence` table.

### MCP Server

Provides Model Context Protocol endpoints for AI/LLM agents to interact with the SENTINEL PRIME system:
- `/mcp/health` - Health check
- `/mcp/agent` - Agent information and capabilities
- `/mcp/task` - Submit tasks for processing (network scans, threat intel updates, etc.)
- `/mcp/task/{task_id}` - Retrieve task status and results

## Database Models

- `Device`: Represents a device on the network (MAC, IP, hostname, vendor, timestamps)
- `ThreatIntelligence`: Stores indicators of compromise (IOCs) from various sources
- `ScanResult`: Stores results of scans performed on devices (to be implemented)

## API Endpoints

- `GET /`: Returns a welcome message
- `GET /health`: Health check endpoint

## MCP Endpoints

- `GET /mcp/health` → Returns `{"status":"healthy","service":"mcp"}`
- `GET /mcp/agent` → Returns agent information including name, version, and capabilities
- `POST /mcp/task` → Accepts task submissions from AI agents
- `GET /mcp/task/{task_id}` → Retrieves task status and results

## Future Work

- Implement actual scanning triggers when new devices are detected
- Add more threat intelligence feeds
- Implement a web interface or additional API endpoints for managing devices and viewing threats
- Add user authentication and authorization
- Implement vector-based similarity search for threat patterns using pgvector
- Enable privileged container mode for network scanning and IDS/IPS execution
- Install required tools (nmap, suricata) in backend container for active scanning
