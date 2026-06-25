# MISP Integration

## Overview

MISP (Malware Information Sharing Platform) is an open-source threat intelligence platform for sharing, storing, and correlating Indicators of Compromise (IOCs).

## Why MISP?

- **Threat intelligence feeds**: Access community-shared IOCs
- **Automatic enrichment**: Enrich events with threat data
- **IOC lookup**: Check IPs, domains, hashes against database
- **Export formats**: Suricata, Snort, OpenIOC
- **Community sharing**: Contribute and receive threat data

## Quick Start

### Docker Deployment

```bash
# Using docker-compose
docker-compose up -d misp

# First-time setup (wait 5 min for initialization)
# Access MISP at https://localhost:9443
# Default login: admin@admin.test / admin
```

### Access

- **URL**: https://localhost:9443
- **Default Email**: admin@admin.test
- **Default Password**: admin (change immediately!)
- **Note**: Accept self-signed certificate

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| MISP_ADMIN_EMAIL | Admin email | admin@admin.test |
| MISP_ADMIN_PASSWORD | Admin password | admin |
| MISP_BASE_URL | Base URL | https://localhost:9443 |

### Initial Setup

1. Access MISP web interface
2. Change admin password immediately
3. Configure email (optional)
4. Enable threat feeds:
   - Go to Sync Actions > List Feeds
   - Enable desired feeds (CIRCL, Abuse.ch, etc.)
5. Generate API key for Sentinel Prime

### Getting API Key

1. Log into MISP
2. Go to Automation > List
3. Create new API key
4. Copy key for Sentinel Prime configuration

## API Integration

### Available Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/integrations/misp/lookup/{type}/{value}` | GET | Lookup IOC reputation |
| `/api/integrations/misp/push-event` | POST | Push event to MISP |
| `/api/integrations/misp/feeds` | GET | List available feeds |
| `/api/integrations/misp/events` | GET | List recent events |

### IOC Types Supported

- `ip` - IPv4/IPv6 addresses
- `domain` - Domain names
- `url` - URLs
- `hash` - File hashes (MD5, SHA1, SHA256)
- `email` - Email addresses
- `filename` - File names
- `mutex` - Mutex names

### Example Responses

#### GET /api/integrations/misp/lookup/ip/1.2.3.4
```json
{
  "type": "ip",
  "value": "1.2.3.4",
  "found": true,
  "misp_events": [
    {
      "event_id": 1234,
      "title": "Malicious IP Report",
      "threat_level": "High",
      "tags": ["osint", "botnet"],
      "last_seen": "2026-03-10T12:00:00Z"
    }
  ],
  "related_indicators": {
    "domains": ["malicious-domain.com"],
    "urls": ["http://malicious-domain.com/payload"]
  },
  "recommendation": "block"
}
```

#### GET /api/integrations/misp/lookup/domain/example.com
```json
{
  "type": "domain",
  "value": "example.com",
  "found": false,
  "misp_events": [],
  "recommendation": "allow"
}
```

## Implementation

### Docker Compose Addition

Add to `docker-compose.yml`:

```yaml
  misp:
    image: coolgu/misp
    container_name: sentinel-prime-misp
    ports:
      - "9443:443"
    volumes:
      - misp-data:/var/www/MISP/App/tmp
      - misp-www:/var/www/html
    environment:
      - MISP_ADMIN_EMAIL=admin@sentinel.local
      - MISP_ADMIN_PASSWORD=${MISP_PASSWORD}
    restart: unless-stopped
    networks:
      - sentinel-prime-network
```

### Backend API Module

Create `backend/api/integrations/misp.py`:

```python
from fastapi import APIRouter, HTTPException
from typing import Optional
import httpx
import os

router = APIRouter(prefix="/integrations/misp", tags=["misp"])

MISP_URL = os.getenv("MISP_URL", "https://localhost:9443")
MISP_API_KEY = os.getenv("MISP_API_KEY", "")

headers = {
    "Authorization": MISP_API_KEY,
    "Accept": "application/json",
    "Content-Type": "application/json"
}

@router.get("/lookup/{ioc_type}/{value}")
async def lookup_ioc(ioc_type: str, value: str):
    """Look up an IOC in MISP."""
    valid_types = ["ip", "domain", "url", "hash", "email", "filename"]
    if ioc_type not in valid_types:
        raise HTTPException(400, f"Invalid IOC type. Valid: {valid_types}")
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{MISP_URL}/attributes/restSearch",
            headers=headers,
            json={
                "type": ioc_type,
                "value": value,
                "returnFormat": "json"
            }
        )
        
        if response.status_code != 200:
            raise HTTPException(502, "Failed to connect to MISP")
        
        data = response.json()
        
        if data.get("response", {}).get("Attribute"):
            attributes = data["response"]["Attribute"]
            return {
                "type": ioc_type,
                "value": value,
                "found": True,
                "misp_events": attributes,
                "recommendation": "block" if attributes else "allow"
            }
        
        return {
            "type": ioc_type,
            "value": value,
            "found": False,
            "misp_events": [],
            "recommendation": "allow"
        }

@router.post("/push-event")
async def push_event(event_data: dict):
    """Push a security event to MISP."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{MISP_URL}/events",
            headers=headers,
            json=event_data
        )
        
        if response.status_code == 200:
            return {"status": "success", "event_id": response.json().get("Event", {}).get("id")}
        raise HTTPException(502, "Failed to push event to MISP")

@router.get("/feeds")
async def list_feeds():
    """List available MISP threat feeds."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{MISP_URL}/feeds/index",
            headers=headers
        )
        return response.json()

@router.get("/events")
async def list_events(limit: int = 10):
    """List recent MISP events."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{MISP_URL}/events/index",
            headers=headers,
            params={"limit": limit}
        )
        return response.json()
```

## Use Cases

### 1. Honeypot Event Enrichment

When a honeypot detects an attack:

1. Extract attacker IP
2. Query MISP for reputation
3. If malicious, auto-create alert with MISP tags
4. Optionally share back to MISP community

```python
async def enrich_honeypot_event(ip: str):
    result = await lookup_ioc("ip", ip)
    if result["found"]:
        # Add MISP threat level to alert
        severity = map_misp_threat_to_alert(result["threat_level"])
        create_alert(source="honeypot", severity=severity, 
                     details=f"MISP: {result['misp_events']}")
```

### 2. Proactive Threat Blocking

Periodically fetch high-confidence IOCs:

1. Query MISP for critical threats
2. Update firewall rules
3. Alert on new threats

### 3. Threat Intelligence Sharing

Share discovered threats:

1. Detect suspicious activity
2. Create MISP event with IOCs
3. Share with community (if configured)

## Recommended Feeds

Enable these community feeds:

| Feed | Description | Update Frequency |
|------|-------------|-----------------|
| CIRCL OSINT | Community OSINT | 1 hour |
| Abuse.ch Feodo Tracker | Botnet C&C | 1 hour |
| Abuse.ch URLhaus | Malware URLs | 15 min |
| Abuse.ch SSL Blacklist | Malicious SSL | 1 hour |
| DShield | ISC threats | 1 hour |

## Troubleshooting

### Cannot access MISP
- Wait 5 minutes for initial setup
- Check container logs: `docker logs misp`
- Verify SSL certificate acceptance

### API key not working
- Regenerate API key in MISP web UI
- Verify key has correct permissions

### Feed sync failing
- Check network connectivity
- Verify feed URLs are accessible
- Check MISP logs for errors

## Security Considerations

1. **Change default password** immediately
2. **Use strong API keys**
3. **Enable HTTPS** in production
4. **Configure feed authentication** where available
5. **Review sharing settings** before enabling community sharing
6. **Regular backups** of MISP data

## Resources

- [MISP Official Website](https://www.misp-project.org/)
- [MISP Docker](https://hub.docker.com/r/coolgu/misp)
- [MISP Documentation](https://www.misp-project.org/documentation/)
- [MISP API](https://www.misp-project.org/openapi/)

---

*Last Updated: March 2026*
