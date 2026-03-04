# Network Scanner (Nmap/OpenVAS)

## Purpose
Scan network for devices, open ports/services, and associate with device names.

## Getting Started
- Launch via Docker Compose, configure via UI
- See ADR.md for architecture

## API/Integration
- Scans triggered by UI or new device monitor.
- Results stored in database, shown via UI.

## Contributing
- Script new scan modes, improve device fingerprinting, add security checks.
