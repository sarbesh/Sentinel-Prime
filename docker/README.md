# Docker/Orchestration

## Purpose
Containerize and orchestrate all modules for easy deployment, upgrades, and modular dev.

## Quickstart

### Build and Run
```bash
# Build and start all services
docker-compose up --build

# Run in background
docker-compose up -d --build

# View logs
docker-compose logs -f

# Stop all services
docker-compose down
```

### Development
The backend is currently the only active service. Other modules (network-scanner, honeypot, ips-ids) are placeholders waiting for implementation.

## Services

### Backend
- **Image**: Python 3.12-slim
- **Port**: 8000
- **Healthcheck**: `/health` endpoint
- **Volume**: SQLite database persists in named volume

## API/Integration
- Compose dependencies, volumes, networks as needed
- All services share `sentinel-prime-network` bridge network

## Contributing
- Improve resource use, add healthchecks, new containers/modules
- When adding new modules, add their Dockerfile and compose service

---

*Last updated: 2026-03-04*
