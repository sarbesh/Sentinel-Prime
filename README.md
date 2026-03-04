# SENTINEL PRIME

## Overview

SENTINEL PRIME is an open-source, sci-fi-inspired, modular honeypot and network threat monitoring suite for home networks.

Runs on Raspberry Pi, laptops, or containers. Unified web/mobile UI (React Native). Each tool and module is independent and documented—so any human or AI can pick up, work, and understand the project at any stage.

Dedicated to modularity, clarity, and evolution—community contributions are highly encouraged, and the entire project is open for change at any time.

---

## Architecture Diagram (ASCII)

```
+-----------------------+    +---------------------+
|  Home Network Devices |<-> |       Router/GW     |
+-----------------------+    +---------------------+
         |                           |
         v                           v
+-----------------------+    +---------------------+
|     DHCP Listener     |    |  IPS/IDS (Suricata, |
|  (detect new device)  |    |     Zeek)           |
+-----------------------+    +---------------------+
         |                           |
         v                           v
+-------------------+         +---------------+
| Network Scanner   |         | Honeypot      |
| (Nmap/OpenVAS)   |         | (OpenCanary/  |
|                  |         | Dionaea)      |
+-------------------+         +---------------+
         |                           |
         +-----------+---------------+
                     v
         +---------------------------+
         |     Backend/API           |
         +--------+------------------+
                  |
     +------------+------------+
     | Web & Mobile Unified UI |
     |   (React Native/App     |
     |    Web via PWA?)        |
     +------------+------------+
                  |
              +---+---+
              | DB    |
              +-------+
         | Threat Feeds (OTX etc.) |
         | Reporting & Notification|
         +------------------------+
```

---

## Key Points
- Modular: Each component in a Docker container, orchestrated by Compose
- Unified UI: React Native (web, mobile from one codebase)
- Extensible: Add/replace modules easily (scanner, honeypot, IDS/IPS, etc)
- Privacy/security first
- Open to changes, feature requests, and community contributions at any time

---

## Getting Started
- See `/docs/getting-started.md` for local bootstrap instructions
- Open, modular design—choose which modules to deploy per your needs

---

## Contributing
- Everyone welcome! See `CONTRIBUTING.md` for how to start.
- Project always open to refactoring, new features, and improvements.
- File issues, feature requests, and pull requests as desired—review and merge process is documented in `/docs/development.md`

---

## License
MIT (see LICENSE)

---

## Roadmap
- [ ] Project structure & scaffolding
- [ ] Unified React Native UI for web/mobile
- [ ] Modular backend and database
- [ ] Network scanner integration
- [ ] New device detection (DHCP)
- [ ] IPS/IDS module
- [ ] Honeypot module
- [ ] Threat intelligence integration
- [ ] Reporting: web/mobile and push notifications

For full TODO see `/docs/roadmap.md`
