# Sentinel Prime

A network security monitoring system with backend API, scanner, vector database, and a cross-platform web UI.

## Overview

Sentinel Prime is a network security monitoring system that provides:
- Device discovery and tracking
- Network scanning capabilities
- Vulnerability detection and management
- Alerting and reporting
- A modern web interface for monitoring and management

## Components

- **Backend**: FastAPI-based API server (`/backend`)
- **Scanner**: Network scanning module (`/scanner`)
- **Vector Database**: PostgreSQL with pgvector for similarity search (`/vector-db` implied)
- **Web UI**: Cross-platform React/Vite TypeScript application (`/web-ui`)
- **MCP Server**: Model Context Protocol server for AI tool integration
- **Additional modules**: DHCP listener, threat intelligence updater, honeypot, IDS/IPS, etc.

## Getting Started

See the individual component READMEs for detailed setup instructions:

- [Backend README](./backend/README.md)
- [Web UI README](./web-ui/README.md)

## Docker Compose

The easiest way to run Sentinel Prime is using Docker Compose:

```bash
docker-compose up -d
```

This will start all services:
- Backend API on http://localhost:8000
- Web UI on http://localhost:3000
- Vector database on http://localhost:5432
- And other supporting services

## API Documentation

Once the backend is running, visit http://localhost:8000/docs for interactive API documentation (Swagger UI).

## License

MIT License - see [LICENSE](./LICENSE) file for details.

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines.

## Code of Conduct

Please review our [Code of Conduct](./CODE_OF_CONDUCT.md).