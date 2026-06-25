# Task/TODO List

## How To Use
- Each task is modular and linked to its module's README and docs.
- Anyone (human or AI) can pick up any task—just read the described files and get started.
- If details are missing, update the documentation as part of the task!

---

### Project Bootstrapping
- [x] Create project structure, LICENSE, README, docs
- [x] Write architecture diagram and ADRs
- [x] Add per-module README files

### Web & Mobile Unified UI (React Native)
- [x] Scaffold React Native codebase under `/web-ui`
- [ ] Login/auth system
- [x] Dashboard, report, and config screens

### Backend/API
- [x] Scaffold basic backend API in `/backend`
- [x] Database setup/migration scripts
- [x] API endpoints for modules

### Network Scanner
- [x] Scaffold Nmap/OpenVAS container in `/network-scanner`
- [x] UI and API integration (scan results)
- [x] Scan network for pingable devices and report
- [x] Scan network with -Pn nmap flag (no ping)
- [x] Perform deep scan on detected hosts
- [x] Check for vulnerable services and exploitation warnings
- [ ] UI integration for vulnerability alerts

### Device Monitor
- [ ] DHCP listener trigger in `/new-device-monitor`
- [ ] Scan-on-connect scripts

### IPS/IDS
- [ ] Scaffold Suricata/Zeek container in `/ips-ids`
- [ ] Alerts to UI/API

### Honeypot
- [ ] Scaffold OpenCanary/Dionaea in `/honeypot`
- [ ] Attack logging, UI/API integration

### Threat Intelligence
- [ ] Feed-updater script in `/threat-intel`
- [ ] Sync with Suricata/Zeek/honeypot rules

### Reporting
- [ ] HTML report generation script(s)
- [ ] Notification setup (UI, push, email)

### Documentation & Maintenance
- [x] Every module must have a README
- [x] ADRs describe key decisions
- [x] Docs updated regularly for clarity

### MCP Server (AI Integration)
- [x] Install MCP dependencies (mcp, sse-starlette)
- [x] Create MCP server module in `/backend/mcp_server/`
- [x] Define MCP tools (list_devices, get_alerts, trigger_scan, etc.)
- [x] Add SSE endpoint to FastAPI main.py
- [x] Add MCP authentication (API key/bearer token)
- [x] Update docker-compose to expose MCP port

### MCP + Kali Linux Integration (Advanced)
See `/docs/kali-mcp-integration.md` for full documentation.

- [ ] Set up Kali MCP server (Docker or native)
- [ ] Create Kali MCP client module in `/backend/mcp/kali_client.py`
- [ ] Add `/mcp/kali/connect` endpoint for Kali server configuration
- [ ] Add `/mcp/kali/execute` endpoint for tool proxy
- [ ] Implement MCP gateway to aggregate tools from multiple servers
- [ ] Add Kali server authentication
- [ ] Update UI for Kali connection configuration
- [ ] Security: Add rate limiting and tool allowlist for Kali tools
- [ ] Test full workflow: AI → Sentinel → Kali tools

### AI Threat Detection (Future)
- [ ] Design AI module architecture
- [ ] Implement data pipeline for ML model input
- [ ] Deploy anomaly detection model (Isolation Forest/XGBoost)
- [ ] Integrate LLM for threat analysis
- [ ] Add AI insights to UI dashboard

### Open Source Tool Integrations
See `/docs/integrations/` for detailed documentation.

#### Phase 1: Network Visualization (Priority #1)
- [ ] Deploy ntopng Docker container
- [ ] Add ntopng configuration (ports, auth)
- [ ] Create `/api/integrations/ntopng/top-hosts` endpoint
- [ ] Create `/api/integrations/ntopng/traffic-stats` endpoint
- [ ] Create `/api/integrations/ntopng/applications` endpoint
- [ ] Integrate ntopng data into dashboard UI

#### Phase 2: Threat Intelligence (Priority #2)
- [ ] Deploy MISP Docker container
- [ ] Configure MISP initial settings (admin, feeds)
- [ ] Create `/api/integrations/misp/lookup/{type}/{value}` endpoint
- [ ] Create `/api/integrations/misp/push-event` endpoint
- [ ] Create `/api/integrations/misp/feeds` endpoint
- [ ] Implement automatic IOC enrichment for honeypot events

#### Phase 3: Lightweight SIEM (Priority #3)
- [ ] Deploy GoAccess Docker container
- [ ] Configure log aggregation
- [ ] Create `/api/metrics/network` endpoint
- [ ] Create `/api/metrics/system` endpoint
- [ ] Integrate metrics into dashboard

#### Phase 4: Home Automation (Priority #4)
- [ ] Deploy Home Assistant Docker container
- [ ] Create Home Assistant API client module
- [ ] Create `/api/integrations/ha/connect` endpoint
- [ ] Create `/api/integrations/ha/notify` endpoint
- [ ] Create `/api/integrations/ha/devices` endpoint
- [ ] Create automation examples (auto-block, notifications)
- [ ] Add HA device status to Sentinel dashboard

---

> Find a task, check its module README and API, and get started. Update documentation as you work!
