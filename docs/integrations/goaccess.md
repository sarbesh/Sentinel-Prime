# GoAccess Integration

## Overview

GoAccess is a real-time web log analyzer and interactive viewer that runs in a terminal or provides a static HTML dashboard.

## Why GoAccess?

- **Lightweight**: ~50MB RAM usage
- **Fast**: C-based, minimal dependencies
- **Real-time**: Live dashboard updates
- **No database**: Works directly with log files
- **Web interface**: Browser-based HTML reports

## Quick Start

### Docker Deployment

```bash
# Using docker-compose
docker-compose up -d goaccess

# Manual
docker run -d \
  --name sentinel-prime-goaccess \
  -p 7890:7890 \
  -v ./logs:/var/log/goaccess \
  allinurl/goaccess \
  -f /var/log/goaccess/access.log \
  --log-format=COMBINED \
  --real-time-html
```

### Access

- **Dashboard**: http://localhost:7890
- **Static Report**: http://localhost:7890/report.html

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| GOACCESS_LOG_PATH | Path to log file | /var/log/goaccess |
| GOACCESS_PORT | HTTP port | 7890 |

### Log Formats

GoAccess supports multiple log formats:

```
# Apache Combined
--log-format=COMBINED

# Apache Common
--log-format=COMMON

# Nginx
--log-format=NGINX

# CloudFront
--log-format=CLOUDFRONT

# AWS Elastic Load Balancing
--log-format=ELB
```

### Custom Configuration

Create `goaccess.conf`:

```conf
# /path/to/goaccess.conf

# Log format
log-format COMBINED

# Time format
time-format %H:%M:%S

# Date format
date-format %d/%b/%Y

# Real-time HTML
real-time-html true

# Static files
static-file .css
static-file .js
static-file .jpg
static-file .png
static-file .ico
static-file .gif
```

## API Integration

### Available Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/metrics/network` | GET | Get network metrics summary |
| `/api/metrics/system` | GET | Get system metrics |
| `/api/metrics/logs` | GET | Get log statistics |

### Custom Metrics Endpoints

Since GoAccess doesn't have a native API, we'll create custom endpoints that parse logs:

```python
# backend/api/integrations/metrics.py

from fastapi import APIRouter
import os
import re
from collections import defaultdict
from datetime import datetime, timedelta

router = APIRouter(tags=["metrics"])

LOG_PATH = os.getenv("GOACCESS_LOG_PATH", "/var/log/goaccess")

def parse_log_line(line: str) -> dict:
    """Parse a standard log line."""
    pattern = r'(\S+) \S+ \S+ \[(\d+/\w+/\d+:\d+:\d+:\d+)\] "(\S+) (\S+) \S+" (\d+) (\d+)'
    match = re.match(pattern, line)
    if match:
        return {
            "ip": match.group(1),
            "timestamp": match.group(2),
            "method": match.group(3),
            "path": match.group(4),
            "status": int(match.group(5)),
            "bytes": int(match.group(6))
        }
    return None

@router.get("/metrics/network")
async def get_network_metrics():
    """Get network traffic metrics from logs."""
    metrics = {
        "total_requests": 0,
        "total_bytes": 0,
        "unique_ips": set(),
        "status_codes": defaultdict(int),
        "top_paths": defaultdict(int),
        "top_ips": defaultdict(int),
    }
    
    try:
        with open(f"{LOG_PATH}/access.log", "r") as f:
            for line in f:
                parsed = parse_log_line(line)
                if parsed:
                    metrics["total_requests"] += 1
                    metrics["total_bytes"] += parsed["bytes"]
                    metrics["unique_ips"].add(parsed["ip"])
                    metrics["status_codes"][parsed["status"]] += 1
                    metrics["top_paths"][parsed["path"]] += 1
                    metrics["top_ips"][parsed["ip"]] += parsed["bytes"]
    except FileNotFoundError:
        return {"error": "Log file not found"}
    
    # Convert sets to lists for JSON
    metrics["unique_ips"] = len(metrics["unique_ips"])
    metrics["top_paths"] = dict(sorted(
        metrics["top_paths"].items(), 
        key=lambda x: x[1], 
        reverse=True
    )[:10])
    metrics["top_ips"] = dict(sorted(
        metrics["top_ips"].items(), 
        key=lambda x: x[1], 
        reverse=True
    )[:10])
    metrics["status_codes"] = dict(metrics["status_codes"])
    
    return metrics

@router.get("/metrics/logs")
async def get_log_stats():
    """Get log file statistics."""
    try:
        stat = os.stat(f"{LOG_PATH}/access.log")
        return {
            "file_size": stat.st_size,
            "last_modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "total_lines": sum(1 for _ in open(f"{LOG_PATH}/access.log")),
        }
    except FileNotFoundError:
        return {"error": "Log file not found"}
```

### Example Responses

#### GET /api/metrics/network
```json
{
  "total_requests": 15420,
  "total_bytes": 52428800,
  "unique_ips": 156,
  "status_codes": {
    "200": 12000,
    "301": 500,
    "404": 2100,
    "500": 120
  },
  "top_paths": {
    "/": 5200,
    "/api/status": 3100,
    "/dashboard": 1800
  },
  "top_ips": {
    "192.168.1.100": 15240000,
    "192.168.1.50": 8200000
  }
}
```

## Implementation

### Docker Compose Addition

```yaml
  goaccess:
    image: allinurl/goaccess
    container_name: sentinel-prime-goaccess
    ports:
      - "7890:7890"
    volumes:
      - ./logs:/var/log/goaccess
      - ./goaccess.conf:/etc/goaccess/goaccess.conf
    command: >
      -f /var/log/goaccess/access.log
      --log-format=COMBINED
      --real-time-html
      --ws-url=ws://localhost:7890
    restart: unless-stopped
    networks:
      - sentinel-prime-network
```

### Log Aggregation Setup

To aggregate logs from multiple sources:

1. Create a shared log directory
2. Configure log rotation
3. Point GoAccess to aggregated log

```bash
# Create log directory
mkdir -p logs

# Aggregate logs (example)
tail -f /var/log/nginx/access.log > logs/access.log
tail -f /var/log/apache2/access.log >> logs/access.log

# Or use Docker volumes for log sharing
```

## Dashboard Integration

### Embed GoAccess Dashboard

Add to Sentinel Prime UI:

```javascript
// In dashboard component
<iframe 
  src="http://localhost:7890" 
  width="100%" 
  height="600px" 
  frameBorder="0" 
/>
```

### Custom Sentinel Dashboard

Create custom widgets using metrics API:

```javascript
// Example widget component
const NetworkMetrics = () => {
  const metrics = useFetch('/api/metrics/network');
  
  return (
    <div className="metrics-grid">
      <MetricCard 
        title="Total Requests" 
        value={metrics.total_requests} 
      />
      <MetricCard 
        title="Unique IPs" 
        value={metrics.unique_ips} 
      />
      <MetricCard 
        title="Error Rate" 
        value={(metrics.status_codes[500] / metrics.total_requests * 100).toFixed(2)} 
        suffix="%"
      />
    </div>
  );
};
```

## Troubleshooting

### No data displayed
- Verify log file exists: `docker exec goaccess ls -la /var/log/goaccess`
- Check log format matches configuration
- Ensure log file has correct permissions

### WebSocket errors
- Verify port 7890 is accessible
- Check GoAccess version supports real-time

### High memory usage
- Enable log rotation
- Limit log file size
- Use --no-panel for specific panels

## Log Rotation

Configure log rotation to prevent disk full:

```conf
# /etc/logrotate.d/goaccess
/var/log/goaccess/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 0640 root root
    postrotate
        docker restart goaccess
    endscript
}
```

## Alternative: Lightweight Alternatives

If GoAccess doesn't meet needs:

| Tool | Description | Resources |
|------|-------------|-----------|
| **Glances** | Cross-platform monitoring | ~100MB |
| **Netdata** | Real-time monitoring | ~150MB |
| **Prometheus + Grafana** | Full metrics stack | ~500MB |

## Security Considerations

1. **Restrict network access** to dashboard
2. **Enable authentication** via reverse proxy
3. **Use HTTPS** in production
4. **Rotate logs** regularly
5. **Monitor disk usage**

## Resources

- [GoAccess Official Website](https://goaccess.io/)
- [GoAccess Documentation](https://goaccess.io/get-started)
- [Docker Hub](https://hub.docker.com/r/allinurl/goaccess)
- [Configuration Options](https://goaccess.io/manpage)

---

*Last Updated: March 2026*
