# ntopng Integration

## Overview

ntopng is a high-speed web-based traffic analysis and flow collection tool that provides 360° network visibility.

## Why ntopng?

- **Real-time traffic visualization**: See what's happening on your network
- **Top talkers**: Identify bandwidth-heavy devices
- **Application detection**: Detect apps (YouTube, Netflix, BitTorrent, etc.)
- **Historical data**: Track traffic patterns over time
- **Lightweight**: Efficient C-based implementation

## Quick Start

### Docker Deployment

```bash
# Using docker-compose
docker-compose up -d ntopng

# Manual
docker run -d \
  --name sentinel-prime-ntopng \
  -p 4000:3000 \
  -v ntopng-data:/var/lib/ntopng \
  -e NTOPNG_HTTP_PORT=3000 \
  -e NTOPNG_ADMIN_USER=admin \
  -e NTOPNG_ADMIN_PASSWORD=ntoppassword \
  ntopng/ntopng
```

### Access

- **URL**: http://localhost:4000
- **Default User**: admin
- **Default Password**: ntoppassword (change!)

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| NTOPNG_HTTP_PORT | HTTP port | 3000 |
| NTOPNG_ADMIN_USER | Admin username | admin |
| NTOPNG_ADMIN_PASSWORD | Admin password | (none) |

### Connecting to Network Tap

For full traffic analysis, connect ntopng to a network tap or mirror port:

```yaml
ntopng:
  image: ntopng/ntopng
  ports:
    - "4000:3000"
  volumes:
    - ntopng-data:/var/lib/ntopng
  environment:
    - NTOPNG_HTTP_PORT=3000
    - NTOPNG_ADMIN_USER=admin
    - NTOPNG_ADMIN_PASSWORD=${NTOPNG_PASSWORD}
  command: "-i eth0"  # Network interface for mirroring
```

## API Integration

### Available Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/integrations/ntopng/top-hosts` | GET | Get top bandwidth consumers |
| `/api/integrations/ntopng/traffic-stats` | GET | Get traffic statistics |
| `/api/integrations/ntopng/applications` | GET | Get application breakdown |
| `/api/integrations/ntopng/flows` | GET | Get active flows |

### Example Responses

#### GET /api/integrations/ntopng/top-hosts
```json
{
  "hosts": [
    {
      "ip": "192.168.1.1",
      "name": "router",
      "bytes_sent": 1024000,
      "bytes_received": 2048000,
      "throughput": 150.5
    },
    {
      "ip": "192.168.1.100",
      "name": "laptop",
      "bytes_sent": 512000,
      "bytes_received": 768000,
      "throughput": 75.2
    }
  ]
}
```

#### GET /api/integrations/ntopng/traffic-stats
```json
{
  "total_bytes": 15728640,
  "total_packets": 12580,
  "peak_throughput": 250.5,
  "avg_throughput": 85.3,
  "active_flows": 42
}
```

## Implementation

### Docker Compose Addition

Add to `docker-compose.yml`:

```yaml
  ntopng:
    image: ntopng/ntopng
    container_name: sentinel-prime-ntopng
    ports:
      - "4000:3000"
    volumes:
      - ntopng-data:/var/lib/ntopng
    environment:
      - NTOPNG_HTTP_PORT=3000
      - NTOPNG_ADMIN_USER=admin
      - NTOPNG_ADMIN_PASSWORD=${NTOPNG_PASSWORD}
    restart: unless-stopped
    networks:
      - sentinel-prime-network
```

### Backend API Module

Create `backend/api/integrations/ntopng.py`:

```python
from fastapi import APIRouter, HTTPException
import httpx

router = APIRouter(prefix="/integrations/ntopng", tags=["ntopng"])

NTOPNG_URL = "http://ntopng:3000"
NTOPNG_USER = os.getenv("NTOPNG_USER", "admin")
NTOPNG_PASS = os.getenv("NTOPNG_PASS", "ntoppassword")

@router.get("/top-hosts")
async def get_top_hosts(limit: int = 10):
    """Get top bandwidth-consuming hosts."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{NTOPNG_URL}/api/getTopHosts",
            params={"limit": limit},
            auth=(NTOPNG_USER, NTOPNG_PASS)
        )
        return response.json()

@router.get("/traffic-stats")
async def get_traffic_stats():
    """Get overall traffic statistics."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{NTOPNG_URL}/api/getTrafficStats",
            auth=(NTOPNG_USER, NTOPNG_PASS)
        )
        return response.json()

@router.get("/applications")
async def get_applications():
    """Get application protocol breakdown."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{NTOPNG_URL}/getApps",
            auth=(NTOPNG_USER, NTOPNG_PASS)
        )
        return response.json()
```

## Features

### Dashboard Widgets

Integrate ntopng data into Sentinel Prime dashboard:

1. **Bandwidth Usage**: Real-time throughput graph
2. **Top Devices**: Table of highest bandwidth consumers
3. **App Distribution**: Pie chart of protocols/apps
4. **Traffic Timeline**: Historical bandwidth chart

### Alerts

Configure alerts for:
- Unusual bandwidth spike
- New device detected
- Suspicious protocol usage
- High traffic from unknown device

## Troubleshooting

### Cannot connect to ntopng
- Check if container is running: `docker logs ntopng`
- Verify network connectivity between containers
- Check firewall rules

### No traffic data
- Ensure network tap/mirror is configured
- Verify interface name in ntopng command

### Authentication errors
- Reset admin password: `docker exec ntopng ntopng-tool -p reset`

## Security Considerations

1. **Change default password** immediately
2. **Use HTTPS** in production (configure SSL)
3. **Restrict access** via firewall
4. **Enable authentication** for all endpoints
5. **Regular backups** of ntopng data

## Resources

- [ntopng Official Website](https://www.ntop.org/products/traffic-analysis/ntopng/)
- [ntopng Documentation](https://www.ntop.org/guides/ntopng/)
- [Docker Hub](https://hub.docker.com/r/ntopng/ntopng)

---

*Last Updated: March 2026*
