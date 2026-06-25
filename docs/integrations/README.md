# Sentinel Prime Integrations

This directory contains documentation for open-source tool integrations that enhance Sentinel Prime's capabilities.

## Overview

Sentinel Prime integrates with several open-source tools to provide comprehensive network security monitoring:

| Integration | Purpose | Priority | Status |
|-------------|---------|----------|--------|
| [ntopng](./ntopng.md) | Network traffic visualization | #1 | Planned |
| [MISP](./misp.md) | Threat intelligence | #2 | Planned |
| [GoAccess](./goaccess.md) | Lightweight log analysis | #3 | Planned |
| [Home Assistant](./home-assistant.md) | Home automation | #4 | Planned |

## Quick Start

### Deploy All Integrations

```bash
cd /path/to/sentinel-prime
docker-compose -f docker-compose.integrations.yml up -d
```

### Deploy Specific Integration

```bash
# Network visualization
docker-compose up -d ntopng

# Threat intelligence
docker-compose up -d misp

# Log analysis
docker-compose up -d goaccess

# Home automation
docker-compose up -d homeassistant
```

## API Endpoints

All integrations expose REST API endpoints:

```
/api/integrations/ntopng/...
/api/integrations/misp/...
/api/integrations/ha/...
/api/metrics/...
```

## Configuration

Each integration can be configured via:
- Environment variables in docker-compose
- Settings API endpoints
- Web UI (future)

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Sentinel Prime                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐  │
│  │   Backend   │  │   MCP API   │  │   UI Dashboard  │  │
│  └──────┬──────┘  └──────┬──────┘  └────────┬────────┘  │
│         │                │                  │           │
│         └────────────────┴──────────────────┘           │
│                          │                              │
└──────────────────────────┼──────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
┌───────────────┐  ┌─────────────┐  ┌────────────────┐
│    ntopng     │  │    MISP    │  │  Home Assistant │
│  Port: 4000   │  │  Port: 9443│  │   Port: 8123   │
└───────────────┘  └─────────────┘  └────────────────┘
        │                  │                  │
        └──────────────────┼──────────────────┘
                           │
                           ▼
                   ┌───────────────┐
                   │   GoAccess    │
                   │   Port: 7890 │
                   └───────────────┘
```

## Adding New Integrations

To add a new integration:

1. Create a new markdown file in this directory
2. Add the tool to the table above
3. Create API endpoints in `/backend/api/integrations/`
4. Add Docker service to `docker-compose.yml`
5. Update this index file

---

*For detailed documentation, see each integration's markdown file.*
