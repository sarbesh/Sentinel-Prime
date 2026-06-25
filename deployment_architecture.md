# SENTINEL PRIME Deployment Architecture

## Overview

This document describes the deployment architecture for SENTINEL PRIME, covering both microservices (using Docker Compose) and standalone deployment options. The goal is to ensure all features (backend API, UI, scanner, honeypot, IPS/IDS, vector DB, etc.) are available and functional in both modes.

## 1. Microservices Architecture (Docker Compose)

Based on the project verification and structure, the microservices architecture consists of the following services:

### Core Services
- **backend-api**: FastAPI application providing RESTful API, authentication, device management, scanning, alerts, honeypot, IPS/IDS, settings, SSE, etc.
- **database**: PostgreSQL with pgvector extension for vector storage (or SQLite for lightweight deployments)
- **web-ui**: React-based frontend dashboard
- **mobile-app**: React Native mobile application (separate build target)

### Module Services (may run as separate containers or be integrated into backend)
- **network-scanner**: Nmap-based scanning engine
- **honeypot**: OpenCanary-based honeypot for detecting malicious activity
- **ips-ids**: Suricata-based intrusion detection/prevention system
- **mcp-server**: Model Context Protocol server for AI integration
- **arp-monitor**: ARP-based device monitoring (could be a sidecar or integrated)

### Supporting Services
- **reverse-proxy** (nginx): Handles SSL termination and routing to backend-api and web-ui
- **message-broker** (Redis): For task queuing and real-time updates (if used)

### Example docker-compose.yml Structure (inferred)
```yaml
version: '3.8'
services:
  backend:
    build: ./backend
    ports: ["8000:8000"]
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/sentinel
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis
  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=sentinel
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
    volumes:
      - postgres_data:/var/lib/postgresql/data
  redis:
    image: redis:7-alpine
  webui:
    build: ./web-ui
    ports: ["80:80"]
  mobile-app:
    # Built separately, not typically in docker-compose for development
  network-scanner:
    image: instrumentisto/nmap:latest
    # Runs scanning tasks via API calls
  honeypot:
    image: opencanary/opencanary:latest
    ports: ["64295:64295/udp", "64295:64295/tcp"]
  ips-ids:
    image: jasonish/suricata:latest
    cap_add:
      - NET_ADMIN
    devices:
      - "/dev/net/tun:/dev/net/tun"
  mcp-server:
    build: ./mcp_server
    ports: ["8001:8001"]
  arp-monitor:
    build: ./arp_monitor
    network_mode: host  # Requires host network for ARP monitoring
    privileged: true

volumes:
  postgres_data:
```

## 2. Standalone Deployment Options

For home users or simplified deployments, a standalone mode bundles all necessary components into a single deployable unit. Options include:

### Option 1: Single Container with Process Manager
- **Approach**: Use a base image (e.g., Ubuntu or Alpine) and install all services. Use a process manager like `supervisord` or `s6` to manage multiple processes.
- **Components in Container**:
  - PostgreSQL (with pgvector)
  - Redis (if used for caching/queuing)
  - FastAPI backend (with all modules integrated)
  - Nginx (reverse proxy)
  - Optional: Network scanner, honeypot, IPS/IDS (if host permissions allow)
  - ARP monitor (requires host network or privileged mode)
- **Pros**: Simple deployment (single `docker run`), versioned together.
- **Cons**: Larger image, harder to update individual components, potential conflicts.

### Option 2: Modular Monolith Container
- **Approach**: Keep services as separate processes but within a single container image, using the same base OS. Integrate module functionalities directly into the backend where possible (e.g., embed nmap calls, use Python-based IDS rules).
- **Components**:
  - Single FastAPI application that includes:
    - API endpoints
    - Embedded scanning (via subprocess nmap)
    - Honeypot listener (using asyncio or separate thread)
    - IDS rule engine (simplified, or log-based)
    - Vector store (PostgreSQL connection)
  - Optional: Separate processes for Redis and nginx (or use built-in ASGI server)
- **Pros**: Easier to develop and test, single deployable unit.
- **Cons**: Some modules (like Suricata) require kernel privileges and may not work well embedded; network scanning needs root/raw sockets.

### Option 3: Binary with Embedded Services (Advanced)
- **Approach**: Compile a single binary (e.g., using PyInstaller for Python or Go) that includes the backend and lightweight versions of modules.
- **Feasibility**: Complex due to native dependencies (PostgreSQL, nmap, Suricata). Not recommended unless significant refactoring.

### Option 4: Docker Compose with Profile for Standalone
- **Approach**: Use the existing docker-compose but define a `standalone` profile that starts all services on a single host network, minimizing overhead.
- **Example**: Use `docker-compose --profile standalone up` where the profile includes all services but optimizes for single-host (e.g., shared network, no external load balancer).
- **Pros**: Leverages existing compose, easy to switch between modes.
- **Cons**: Still multiple containers.

## 3. Trade-offs

| Aspect                | Microservices (Compose)          | Standalone (Single Container)     |
|-----------------------|----------------------------------|-----------------------------------|
| **Deployment Complexity** | Moderate (multiple images)       | Simple (single image/run)         |
| **Scalability**       | Horizontal scaling per service   | Limited (vertical scaling only)   |
| **Isolation**         | High (service failures isolated) | Lower (shared resources)          |
| **Updates**           | Independent service updates      | Full image update required        |
| **Resource Overhead** | Higher (multiple OS layers)      | Lower (shared base)               |
| **Development**       | Services can be developed separately | Requires careful dependency management |
| **Home User Suitability** | Overkill for small networks    | Ideal for ease of use             |
| **Feature Completeness** | All modules can be fully featured | Some modules may need adaptation  |

## 4. Recommendations

Given the goal of providing all features in both modes, we recommend:

### For Microservices
- Maintain and optimize the existing `docker-compose.yml` (if not present, create one based on the inferred structure).
- Use Docker profiles for different environments (e.g., `dev`, `prod`, `home`).

### For Standalone
- **Adopt Option 1 (Single Container with Supervisord)** for the initial standalone implementation because:
  - It allows each service to run in its native form without code changes.
  - Supervisord provides process management, restart policies, and logging.
  - It is easier to implement incrementally: start with backend and DB, then add other services.
- **Create a Dockerfile** that:
  - Installs PostgreSQL, Redis, nginx, supervisord.
  - Copies the backend code and installs Python dependencies.
  - Adds configuration for each service (network-scanner, honeypot, ips-ids, etc.) as separate programs in supervisord.conf.
  - Exposes necessary ports (API, UI, etc.).
  - Uses a non-root user where possible, but grants necessary capabilities for scanning/IDS (e.g., `--cap-add=NET_ADMIN --net=host` for certain services, or run the container privileged if required for ARP monitoring and raw sockets).

### Prototype Files

#### 1. Dockerfile.standalone
```Dockerfile
# Use Ubuntu as base for easier package installation
FROM ubuntu:22.04

# Install dependencies
RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-venv \
    postgresql postgresql-contrib \
    redis-server \
    nginx \
    supervisor \
    nmap \
    opencanary \
    suricata \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy backend requirements and install Python deps
COPY backend/requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/ ./backend/
COPY web-ui/ ./web-ui/
COPY mcp_server/ ./mcp_server/
COPY network-scanner/ ./network-scanner/
COPY honeypot/ ./honeypot/
COPY ips-ids/ ./ips-ids/
COPY arp_monitor/ ./arp_monitor/

# Create supervisord configuration
RUN mkdir -p /etc/supervisor/conf.d
COPY supervisord.conf /etc/supervisor/supervisord.conf

# Expose ports
EXPOSE 8000 80 64295

# Start supervisord
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/supervisord.conf"]
```

#### 2. supervisord.conf (example)
```ini
[supervisord]
nodaemon=true
logfile=/var/log/supervisor/supervisord.log
logfile_maxbytes=50MB
logfile_backups=10
loglevel=info

[program:postgres]
command=/usr/lib/postgresql/15/bin/postgres -D /var/lib/postgresql/15/main
user=postgres
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/postgres.log

[program:redis]
command=/usr/bin/redis-server --protected-mode no
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/redis.log

[program:backend]
command=/usr/bin/uvicorn backend.main:app --host 0.0.0.0 --port 8000
directory=/app
autostart=true
autorestart=true
stdout_logfile=/var/log/backend.log
stderr_logfile=/var/log/backend_err.log
environment=DATABASE_URL="postgresql://postgres:@db:5432/sentinel",REDIS_URL="redis://localhost:6379"

[program:webui]
command=cd /app/web-ui && npm start  # or serve built files with nginx
autostart=true
autorestart=true
stdout_logfile=/var/log/webui.log
stderr_logfile=/var/log/webui_err.log

[program:network-scanner]
# Example: run a script that listens for scan requests via API
command=/usr/bin/python3 /app/network-scanner/scanner_daemon.py
autostart=true
autorestart=true
stdout_logfile=/var/log/scanner.log
stderr_logfile=/var/log/scanner_err.log

[program:honeypot]
command=/usr/bin/opencanaryd --file /etc/opencanary.conf
autostart=true
autorestart=true
stdout_logfile=/var/log/honeypot.log
stderr_logfile=/var/log/honeypot_err.log

[program:ids]
command=/usr/bin/suricata -c /etc/suricata/suricata.yaml -i eth0 --af-packet
autostart=true
autorestart=true
stdout_logfile=/var/log/ids.log
stderr_logfile=/var/log/ids_err.log
capabilities=NET_ADMIN+ep  # needs NET_ADMIN

[program:arp-monitor]
command=/usr/bin/python3 /app/arp_monitor/monitor.py
autostart=true
autorestart=true
stdout_logfile=/var/log/arp_monitor.log
stderr_logfile=/var/log/arp_monitor_err.log
```

#### 3. docker-compose.override.yml (for enabling standalone mode with profiles)
```yaml
version: '3.8'

services:
  backend:
    build:
      context: .
      dockerfile: Dockerfile.standalone
    ports:
      - "8000:8000"
      - "80:80"
      - "64295:64295"
    # If needed for ARP monitoring and raw sockets:
    # cap_add:
    #   - NET_ADMIN
    #   - SYS_RAWIO
    # network_mode: host  # Uncomment if required for ARP scanning and IDS
    # privileged: true    # Alternative to cap_add

profiles:
  standalone:
    services:
      # All services are included in the single container, so no extra services needed
      pass

  microservices:
    # Use the original microservices compose (to be defined in docker-compose.yml)
    # This profile would override to use the separate services
    # For brevity, assume docker-compose.yml defines the microservices
    pass
```

## 5. Implementation Notes

- **Database**: In standalone mode, PostgreSQL runs in the same container. For persistence, use a Docker volume mounted to `/var/lib/postgresql/data`.
- **Network Scanning**: Requires `NET_ADMIN` capability or running the container privileged. Alternatively, the scan service can be configured to use `nmap` via sudo if the container runs as a non-root user with appropriate sudoers.
- **IDS/IPS**: Suricata needs `NET_ADMIN` and access to network interfaces. Using `network_mode: host` or `--cap-add=NET_ADMIN` is necessary.
- **ARP Monitor**: Requires access to raw sockets and typically runs best in host network mode.
- **Ports**: Adjust as needed to avoid conflicts on the host.
- **Configuration**: Use environment variables or config files injected via Docker to enable/disable modules (e.g., disable honeypot if not needed).

## 6. Conclusion

SENTINEL PRIME can be deployed effectively in both microservices and standalone modes. The microservices approach offers scalability and isolation, suitable for advanced users or production environments. The standalone approach, particularly using a single container with a process manager, provides simplicity and ease of deployment for home users while maintaining feature completeness.

By providing a Dockerfile and supervisord configuration, users can choose the mode that best fits their needs. Future work should focus on refining the standalone container, ensuring proper logging, security updates, and testing all module integrations within the single container context.

---
*Generated as part of SENTINEL PRIME deployment architecture task.*