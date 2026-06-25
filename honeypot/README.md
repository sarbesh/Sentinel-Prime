# Honeypot Module (OpenCanary)

## Purpose
Emulate vulnerable devices/services, log attack attempts, integrate with threat intelligence and UI.

## Services Emulated
- FTP (port 21)
- SSH (port 22)
- Telnet (port 23)
- HTTP (port 80)
- HTTPS (port 443)
- SMB (port 445)
- MySQL (port 3306)
- PostgreSQL (port 5432)
- Git (port 9418)
- HTTP Title (port 8888)

## Configuration
Edit `config/opencanary.conf` to enable/disable specific services.

## API/Integration
- Logs to backend via `/honeypot/events` API
- Event forwarder monitors `/var/log/opencanary/honeypot.log`
- Attack data stored in `honeypot_events` table

## Deployment
Runs on host network for direct network access:
```bash
docker-compose up -d honeypot
```

## How to contribute
- Update docs, add new protocol emulations, improve attack reporting, or integrate new honeypot tools.
