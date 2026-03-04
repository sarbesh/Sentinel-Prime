# Architecture Overview

## ASCII Diagram

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

## Description
- Each major module is containerized and communicates via API/database.
- All configuration, reporting, and alerts handled via one unified UI (React Native exported to web/mobile).
- Easy to add/extend tools—each module is independently deployable.
- Project always open for refactoring, improvements, and new integrations.

## Future Visualization
- Replace ASCII with SVG/PNG architecture diagram for documentation once modules are defined.
- Keep this file updated as the structure evolves.
