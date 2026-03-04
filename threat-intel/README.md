# Threat Intelligence Module

## Purpose
Fetch and integrate open threat feeds (OTX, AbuseIPDB, ET Open, MISP). Keeps detection rules updated for all scanning/monitor modules.

## Getting Started
- Run updater scripts on schedule or on demand
- See ADR.md for rationale

## API/Integration
- Sync feeds with Suricata/Zeek/honeypot
- Logs and updates stored for learning/reporting

## Contributing
- Add new feeds, optimize syncing, improve threat learning logic.
