# Home Assistant Integration

## Overview

Home Assistant is the world's largest open-source home automation platform. This integration allows Sentinel Prime to send security alerts, control devices, and create automations.

## Why Home Assistant?

- **Extensive integrations**: 3400+ integrations
- **Automation**: Create rules for security responses
- **Notifications**: Multiple notification channels
- **Dashboard**: Custom security dashboards
- **Local control**: Privacy-first, no cloud required

## Architecture

```
┌─────────────────────┐         ┌──────────────────────┐
│   Sentinel Prime    │────────▶│    Home Assistant    │
│                     │   API   │                      │
│  • Security alerts  │         │  • Notifications    │
│  • Device status    │         │  • Automations      │
│  • Threat events    │         │  • Device control   │
└─────────────────────┘         └──────────────────────┘
```

## Quick Start

### Docker Deployment

```bash
# Using docker-compose
docker-compose up -d homeassistant

# Manual
docker run -d \
  --name sentinel-prime-homeassistant \
  --network host \
  -v ha-config:/config \
  -v /etc/localtime:/etc/localtime:ro \
  homeassistant/home-assistant:stable
```

### Access

- **URL**: http://localhost:8123
- **First-time setup**: Complete onboarding in web UI

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| HA_ADMIN_USER | Initial admin user | admin |
| HA_ADMIN_PASSWORD | Initial password | (you choose) |

### First-Time Setup

1. Access Home Assistant at http://localhost:8123
2. Complete onboarding wizard
3. Create account
4. (Optional) Install recommended integrations

### Getting Long-Lived Access Token

For API access:

1. Go to Profile (click user icon)
2. Scroll to "Long-Lived Access Tokens"
3. Click "Create Token"
4. Name: Sentinel Prime
5. Copy the generated token

## API Integration

### Available Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/integrations/ha/connect` | POST | Configure HA connection |
| `/api/integrations/ha/notify` | POST | Send notification |
| `/api/integrations/ha/devices` | GET | Get device states |
| `/api/integrations/ha/events` | GET | Get HA events |

### Configuration Endpoint

```python
@router.post("/integrations/ha/connect")
async def configure_ha(config: HAConfig):
    """Save Home Assistant connection config."""
    settings = {
        "ha_url": config.ha_url,
        "ha_token": config.ha_token,
        "enabled": True
    }
    # Save to database
    return {"status": "configured", "ha_url": config.ha_url}
```

### Notification Endpoint

```python
@router.post("/integrations/ha/notify")
async def send_notification(notification: HANotification):
    """Send notification to Home Assistant."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{HA_URL}/api/services/notify/persistent_notification",
            headers={
                "Authorization": f"Bearer {HA_TOKEN}",
                "Content-Type": "application/json"
            },
            json={
                "title": notification.title,
                "message": notification.message,
                "data": notification.data or {}
            }
        )
        return {"status": "sent"}
```

### Example Requests

#### POST /api/integrations/ha/connect
```json
{
  "ha_url": "http://homeassistant:8123",
  "ha_token": "long-lived-access-token"
}
```

#### POST /api/integrations/ha/notify
```json
{
  "title": "Security Alert",
  "message": "Suspicious activity detected from IP 192.168.1.100",
  "priority": "high",
  "data": {
    "tag": "sentinel-alert-001"
  }
}
```

### Example Responses

#### GET /api/integrations/ha/devices
```json
{
  "devices": [
    {
      "entity_id": "light.living_room",
      "state": "on",
      "attributes": {
        "brightness": 255,
        "friendly_name": "Living Room Light"
      }
    },
    {
      "entity_id": "switch.garage_door",
      "state": "off",
      "attributes": {
        "friendly_name": "Garage Door"
      }
    }
  ]
}
```

## Implementation

### Docker Compose Addition

```yaml
  homeassistant:
    image: homeassistant/home-assistant:stable
    container_name: sentinel-prime-homeassistant
    ports:
      - "8123:8123"
    volumes:
      - ha-config:/config
      - /etc/localtime:/etc/localtime:ro
    environment:
      - TZ=America/New_York
    restart: unless-stopped
    network_mode: host
```

### Backend API Module

Create `backend/api/integrations/home_assistant.py`:

```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import httpx
import os

router = APIRouter(prefix="/integrations/ha", tags=["homeassistant"])

class HAConfig(BaseModel):
    ha_url: str
    ha_token: str

class HANotification(BaseModel):
    title: str
    message: str
    priority: Optional[str] = "normal"
    data: Optional[dict] = None

HA_URL = os.getenv("HA_URL", "")
HA_TOKEN = os.getenv("HA_TOKEN", "")

def get_ha_headers():
    return {
        "Authorization": f"Bearer {HA_TOKEN}",
        "Content-Type": "application/json"
    }

@router.post("/connect")
async def configure_ha(config: HAConfig):
    """Configure Home Assistant connection."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{config.ha_url}/api/",
                headers={"Authorization": f"Bearer {config.ha_token}"}
            )
            if response.status_code == 200:
                # Save config to database
                return {"status": "connected", "ha_url": config.ha_url}
        except:
            pass
    raise HTTPException(400, "Failed to connect to Home Assistant")

@router.post("/notify")
async def send_notification(notification: HANotification):
    """Send notification to Home Assistant."""
    if not HA_URL or not HA_TOKEN:
        raise HTTPException(400, "Home Assistant not configured")
    
    # Map priority to Home Assistant
    priority_map = {
        "high": "high",
        "normal": "normal", 
        "low": "low"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{HA_URL}/api/services/notify/persistent_notification",
            headers=get_ha_headers(),
            json={
                "title": f"🔒 {notification.title}",
                "message": notification.message,
                "data": {
                    "tag": f"sentinel-{notification.priority}",
                    "priority": priority_map.get(notification.priority, "normal")
                }
            }
        )
        
        if response.status_code == 200:
            return {"status": "sent"}
        raise HTTPException(502, "Failed to send notification")

@router.get("/devices")
async def get_devices():
    """Get all device states from Home Assistant."""
    if not HA_URL or not HA_TOKEN:
        raise HTTPException(400, "Home Assistant not configured")
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{HA_URL}/api/states",
            headers=get_ha_headers()
        )
        
        if response.status_code == 200:
            states = response.json()
            # Filter to relevant security devices
            security_entities = [
                s for s in states 
                if s["entity_id"].startswith(("binary_sensor.", "switch.", 
                    "lock.", "camera.", "light."))
            ]
            return {"devices": security_entities}
        raise HTTPException(502, "Failed to get devices")

@router.get("/events")
async def get_events(limit: int = 10):
    """Get recent Home Assistant events."""
    if not HA_URL or not HA_TOKEN:
        raise HTTPException(400, "Home Assistant not configured")
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{HA_URL}/api/events",
            headers=get_ha_headers()
        )
        
        if response.status_code == 200:
            events = response.json()
            return {"events": events[-limit:]}
        raise HTTPException(502, "Failed to get events")

@router.post("/automation/trigger")
async def trigger_automation(automation_id: str):
    """Trigger a Home Assistant automation."""
    if not HA_URL or not HA_TOKEN:
        raise HTTPException(400, "Home Assistant not configured")
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{HA_URL}/api/services/automation/trigger",
            headers=get_ha_headers(),
            json={"entity_id": f"automation.{automation_id}"}
        )
        
        if response.status_code == 200:
            return {"status": "triggered", "automation": automation_id}
        raise HTTPException(502, "Failed to trigger automation")
```

## Automation Examples

### 1. Security Alert Notification

In Home Assistant:

```yaml
automation:
  - alias: Sentinel Security Alert
    trigger:
      - platform: event
        event_type: sentinel_alert
    action:
      - service: notify.persistent_notification
        data:
          title: "🔒 Security Alert"
          message: "{{ trigger.event.data.message }}"
      - service: light.turn_on
        target:
          entity_id: light.living_room
        data:
          flash: short
```

### 2. Auto-Block Suspicious IP

```yaml
automation:
  - alias: Sentinel Auto-Block
    trigger:
      - platform: event
        event_type: sentinel_high_threat
    action:
      - service: switch.turn_off
        target:
          entity_id: switch.guest_network
      - service: notify.mobile_app
        data:
          message: "Suspicious activity detected - Guest network blocked"
```

### 3. Camera Snapshot on Detection

```yaml
automation:
  - alias: Sentinel Camera Snapshot
    trigger:
      - platform: event
        event_type: sentinel_alert
    condition:
      - condition: state
        entity_id: camera.front_door
        state: unavailable
    action:
      - service: camera.snapshot
        target:
          entity_id: camera.front_door
        data:
          filename: "/config/www/sentinel-{{ now() }}.jpg"
```

### 4. Discord/Telegram Notifications

Add to `configuration.yaml`:

```yaml
notify:
  - name: discord
    platform: discord
    api_key: YOUR_DISCORD_API_KEY
    id: YOUR_CHANNEL_ID
    
  - name: telegram
    platform: telegram
    chat_id: YOUR_CHAT_ID
    api_key: YOUR_API_KEY
```

Then use in automations:

```yaml
action:
  - service: notify.discord
    data:
      message: "🔒 Security Alert from Sentinel Prime"
```

## Dashboard Integration

### Custom Sentinel Dashboard Card

Create custom card in Home Assistant:

```yaml
type: custom:stack-in-card
title: 🔒 Sentinel Prime
cards:
  - type: entities
    entities:
      - entity: sensor.sentinel_alerts
        name: Active Alerts
      - entity: sensor.sentinel_devices
        name: Monitored Devices
      - entity: sensor.sentinel_threat_level
        name: Threat Level
  - type: picture-entity
    entity: camera.sentinel_live
    name: Network Map
```

### Sentineld Dashboard in HA

```javascript
// Custom Sentinel Dashboard
const SentinelDashboard = () => {
  const alerts = useHAEntity('sensor.sentinel_alerts');
  const devices = useHAEntity('sensor.sentinel_devices');
  const threatLevel = useHAEntity('sensor.sentinel_threat_level');
  
  return (
    <div className="dashboard">
      <AlertPanel alerts={alerts} />
      <DeviceList devices={devices} />
      <ThreatMeter level={threatLevel} />
    </div>
  );
};
```

## Troubleshooting

### Cannot connect to Home Assistant
- Verify URL is accessible: `curl http://homeassistant:8123`
- Check token is valid
- Ensure both containers on same network

### Notifications not working
- Check Home Assistant logs
- Verify notify service is loaded
- Test with HA developer tools

### Automations not triggering
- Verify automation is enabled
- Check trigger configuration
- Review HA automation traces

## MQTT Integration (Alternative)

For event-driven integration:

```yaml
# Home Assistant MQTT configuration
mqtt:
  sensor:
    - name: Sentinel Alert
      state_topic: "sentinel/alerts"
      json_attributes_topic: "sentinel/alerts/attributes"
```

Then in Sentinel:

```python
import paho.mqtt.client as mqtt

def publish_alert(alert):
    client = mqtt.Client()
    client.connect("homeassistant", 1883)
    client.publish("sentinel/alerts", alert)
```

## Security Considerations

1. **Use Long-Lived Tokens** instead of password
2. **Enable HTTPS** in production
3. **Restrict API access** via firewall
4. **Review automation permissions**
5. **Regular token rotation**
6. **Enable 2FA** on Home Assistant

## Resources

- [Home Assistant Official](https://www.home-assistant.io/)
- [Home Assistant API](https://developers.home-assistant.io/docs/api/)
- [HA Docker](https://www.home-assistant.io/docs/installation/docker/)
- [Community Forums](https://community.home-assistant.io/)

---

*Last Updated: March 2026*
